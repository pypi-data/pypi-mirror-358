from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd

from psql_plugin_artema.application.schemas.psql_connector_service_schemas import ShowTablesParams, GetColumnsParams, \
    AsyncExecuteQueryParams


class IAsyncPSQLPort(ABC):
    @abstractmethod
    async def list_databases(self) -> List[str]: ...

    @abstractmethod
    async def list_schemas(self) -> List[str]: ...

    @abstractmethod
    async def list_tables(self, params: ShowTablesParams) -> List[str]: ...

    @abstractmethod
    async def get_columns(self, params: GetColumnsParams) -> List[Dict[str, Any]]: ...

    @abstractmethod
    async def execute_query(self, params: AsyncExecuteQueryParams) -> List[Dict[str, Any]]: ...

    @abstractmethod
    async def read_table_chunk(
            self, schema: str, table: str,
            limit: int, offset: int,
            order_by: Optional[str]
    ) -> pd.DataFrame: ...

    @abstractmethod
    async def count_rows(self, params: GetColumnsParams) -> int: ...

    @abstractmethod
    async def close(self) -> None: ...
