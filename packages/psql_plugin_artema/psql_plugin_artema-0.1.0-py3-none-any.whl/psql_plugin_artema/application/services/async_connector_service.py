import pandas as pd
from typing import List, Dict, Any, Optional, Generator
from pydantic import validate_call, Field
from typing import Annotated

from psql_plugin_artema.application.interfaces.async_psql_port import IAsyncPSQLPort
from psql_plugin_artema.application.schemas.psql_connector_service_schemas import ShowTablesParams, GetColumnsParams, \
    AsyncExecuteQueryParams


class AsyncPSQLConnectorService:
    def __init__(self, port: IAsyncPSQLPort):
        self._port = port

    @validate_call
    async def list_databases(self) -> List[str]:
        return await self._port.list_databases()

    @validate_call
    async def list_schemas(self) -> List[str]:
        return await self._port.list_schemas()

    @validate_call
    async def list_tables(
        self,
        params: ShowTablesParams
    ) -> List[str]:
        return await self._port.list_tables(params)

    @validate_call
    async def get_columns(
        self,
        params: GetColumnsParams
    ) -> List[Dict[str, Any]]:
        return await self._port.get_columns(params)

    @validate_call
    async def count_rows(self, params: GetColumnsParams):
        return await self._port.count_rows(params)

    @validate_call
    async def execute_query(
        self,
        params: AsyncExecuteQueryParams
    ) -> List[Dict[str, Any]]:
        return await self._port.execute_query(params)

    @validate_call
    async def read_table_in_chunks(
        self,
        table: Annotated[str, Field(min_length=1)],
        chunk_size: Annotated[int, Field(gt=0)],
        schema: Annotated[str, Field(min_length=1)] = 'public',
        order_by: Optional[Annotated[str, Field(min_length=1)]] = None
    ) -> Generator[pd.DataFrame, None, None]:
        offset = 0
        while True:
            df = await self._port.read_table_chunk(
                schema, table, limit=chunk_size,
                offset=offset, order_by=order_by
            )
            if df.empty:
                break
            yield df
            offset += chunk_size
