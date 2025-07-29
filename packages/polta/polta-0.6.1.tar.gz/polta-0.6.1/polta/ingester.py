import polars as pl

from dataclasses import dataclass, field
from datetime import datetime, UTC
from deltalake import DeltaTable, Field, Schema
from os import listdir, path
from polars import DataFrame
from polars.datatypes import DataType, List, String, Struct
from typing import Optional
from uuid import uuid4

from polta.enums import DirectoryType, PipeType, RawFileType, WriteLogic
from polta.exceptions import DirectoryTypeNotRecognized
from polta.maps import Maps
from polta.table import Table
from polta.types import RawMetadata
from polta.udfs import file_path_to_json, file_path_to_payload


@dataclass
class Ingester:
  """Dataclass for ingesting files into the target table
  
  Positional Args:
    table (Table): the target table for ingestion
    directory_type (DirectoryType): the kind of source directory to ingest
    raw_file_type (RawFileType): the format of the source files
  
  Optional Args:
    write_logic (WriteLogic): how to save the data (default APPEND)
  
  Initialized Fields:
    pipe_type (PipeType): what kind of pipe this is (i.e., INGESTER)
    raw_polars_schema (dict[str, DataType]): a polars version of the table's raw schema
    payload_field (Field): the deltalake field of the payload column
    simple_payload (bool): indicates whether the load is simple
    metadata_schema (Schema): the deltalake fields for the raw layer
    payload_schema (dict[str, DataType]): the polars fields for a simple ingestion
  """
  table: Table
  directory_type: DirectoryType
  raw_file_type: RawFileType
  write_logic: WriteLogic = field(default_factory=lambda: WriteLogic.APPEND)

  pipe_type: PipeType = field(init=False)
  raw_polars_schema: dict[str, DataType] = field(init=False)
  payload_field: Field = field(init=False)
  simple_payload: bool = field(init=False)
  metadata_schema: Schema = field(init=False)
  payload_schema: dict[str, DataType] = field(init=False)

  def __post_init__(self) -> None:
    self.pipe_type: PipeType = PipeType.INGESTER
    self.raw_polars_schema: dict[str, DataType] = Maps \
      .deltalake_schema_to_polars_schema(self.table.raw_schema)
    self.payload_field: Field = Field('payload', 'string')
    self.simple_payload: bool = self.table.raw_schema.fields == [self.payload_field]
    self.metadata_schema: list[Field] = Maps.QUALITY_TO_METADATA_COLUMNS['raw']
    self.payload_schema: dict[str, DataType] = Maps.deltalake_schema_to_polars_schema(
      schema=Schema(self.metadata_schema + [self.payload_field])
    )

  def get_dfs(self) -> dict[str, DataFrame]:
    """Ingests new files into the target table"""
    df: DataFrame = self._get_metadata()
    df = self._filter_by_history(df)
    return {self.table.id: self._ingest_files(df)}

  def transform(self, dfs: dict[str, DataFrame]) -> DataFrame:
    """Returns the target table DataFrame from dfs
    
    Args:
      dfs (dict[str, DataFrame]): the DataFrames to transform
    
    Returns:
      df (DataFrame): the resulting DataFrame
    """
    return dfs[self.table.id]

  def export(self, df: DataFrame) -> Optional[str]:
    """Exports the DataFrame in a desired format

    This method is unused for ingesters

    Args:
      df (DataFrame): the DataFrame to export
    """
    return None

  def _get_file_paths(self) -> list[str]:
    """Retrieves a list of file paths based on ingestion parameters
        
    Returns:
      file_paths (list[str]): the resulting applicable file paths
    """
    if self.directory_type.value == DirectoryType.SHALLOW.value:
      return [
        path.join(self.table.ingestion_zone_path, f)
        for f in listdir(self.table.ingestion_zone_path)
      ]
    elif self.directory_type.value == DirectoryType.DATED.value:
      file_paths: list[str] = []
      for date_str in listdir(self.table.ingestion_zone_path):
        file_paths.extend([
          path.join(self.table.ingestion_zone_path, date_str, f)
          for f in listdir(path.join(self.table.ingestion_zone_path, date_str))
        ])
      return file_paths
    else:
      raise DirectoryTypeNotRecognized(self.directory_type)

  def _get_metadata(self) -> DataFrame:
    """Retrieves source file metadata as a DataFrame
        
    Returns:
      df (DataFrame): the metadata DataFrame
    """
    file_paths: list[str] = self._get_file_paths()
    metadata: list[RawMetadata] = [self._get_file_metadata(p) for p in file_paths]
    return DataFrame(metadata, schema=self.payload_schema)

  def _filter_by_history(self, metadata: list[RawMetadata]) -> DataFrame:
    """Removes files from ingestion attempt that have already been ingested
    
    Args:
      metadata (list[RawMetadata]): the file metadata to ingest
    
    Returns:
      file_paths (DataFrame): the resulting DataFrame object with the filtered paths
    """
    # Convert the file_paths field into a DataFrame
    paths: DataFrame = DataFrame(metadata, schema=self.payload_schema)

    # Retrieve the history from the target table
    hx: DataFrame = (self.table
      .get(select=['_file_path', '_file_mod_ts'], unique=True)
      .group_by('_file_path')
      .agg(pl.col('_file_mod_ts').max())
    )

    # If there is a quarantine table, add the history from there, too
    if DeltaTable.is_deltatable(self.table.quarantine_path):
      hx_quarantine: DataFrame = (pl.read_delta(self.table.quarantine_path)
        .select('_file_path', '_file_mod_ts')
        .unique()
        .group_by('_file_path')
        .agg(pl.col('_file_mod_ts').max())
      )
      hx: DataFrame = pl.concat([hx, hx_quarantine]).unique()

    # Filter the paths by the temporary history DataFrame
    return (paths
      .join(hx, '_file_path', 'left')
      .filter(
        (pl.col('_file_mod_ts') > pl.col('_file_mod_ts_right')) |
        (pl.col('_file_mod_ts_right').is_null())
      )
      .drop('_file_mod_ts_right')
    )

  def _ingest_files(self, df: DataFrame) -> DataFrame:
    """Ingests files in the DataFrame according to file type / desired output
    
    Args:
      df (DataFrame): the files to load
    
    Returns:
      df (DataFrame): the ingested files
    """
    if self.simple_payload:
      return self._run_simple_load(df)
    elif self.raw_file_type.value == RawFileType.JSON.value:
      return self._run_json_load(df)
    else:
      raise NotImplementedError(self.raw_file_type)

  def _get_file_metadata(self, file_path: str) -> RawMetadata:
    """Retrieves file metadata from a file

    Args:
      file_path (str): the path to the file
    
    Returns:
      raw_metadata (RawMetadata): the resulting raw metadata of the file
    """
    if not path.exists(file_path):
      raise FileNotFoundError()

    return RawMetadata(
      _raw_id=str(uuid4()),
      _ingested_ts=datetime.now(),
      _file_path=file_path,
      _file_name=path.basename(file_path),
      _file_mod_ts=datetime.fromtimestamp(path.getmtime(file_path), tz=UTC)
    )

  def _run_simple_load(self, df: DataFrame) -> DataFrame:
    """Retrieves the payload from the file path for each row
    
    Args:
      df (DataFrame): the data with metadata to load
    
    Returns:
      df (DataFrame): the resulting DataFrame
    """
    return (df
      .with_columns([
        pl.col('_file_path')
          .map_elements(file_path_to_payload, return_dtype=String)
          .alias('payload')
      ])
    )

  def _run_json_load(self, df: DataFrame) -> DataFrame:
    """Retrieves the payload values from the file path for each row
    
    Args:
      df (DataFrame): the data with metadata to load
    
    Returns:
      df (DataFrame): the resulting DataFrame
    """
    df: DataFrame = (df
      .with_columns([
        pl.col('_file_path')
          .map_elements(
            function=file_path_to_json,
            return_dtype=List(Struct(self.raw_polars_schema))
          )
          .alias('payload')
      ])
      .explode('payload')
      .with_columns([
        pl.col('payload').struct.field(f).alias(f)
        for f in self.raw_polars_schema.keys()
      ])
      .drop('payload')
    )
    return df
