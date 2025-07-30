from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Generator

from psql_plugin_artema.application.dtos import ChunkDTO
from psql_plugin_artema.application.schemas.psql_connector_service_schemas import ShowTablesParams, GetColumnsParams, \
    ExecuteQueryParams
from psql_plugin_artema.domain.entities import PSQLColumn


class IPSQLPort(ABC):
    @abstractmethod
    def list_tables(self, params: ShowTablesParams) -> List[str]: pass

    @abstractmethod
    def list_databases(self) -> List[str]: pass

    @abstractmethod
    def get_columns(self, params: GetColumnsParams) -> List[PSQLColumn]: pass

    @abstractmethod
    def run_query(self, params: ExecuteQueryParams) -> List[Dict[str, Any]]: pass

    @abstractmethod
    def run_query_in_chunks(self, params: ExecuteQueryParams) -> Generator[ChunkDTO, None, None]: pass

    @abstractmethod
    def count_rows(self, params: GetColumnsParams) -> int: pass

    @abstractmethod
    def is_distributed(self, table: str) -> bool: pass

    @abstractmethod
    def list_schemas(self) -> List[str]: pass

    @abstractmethod
    def read_table_chunk(
            self,
            table: str,
            limit: int,
            offset: int,
            schema: str,
            order_by: Optional[str] = None
    ) -> ChunkDTO: pass

