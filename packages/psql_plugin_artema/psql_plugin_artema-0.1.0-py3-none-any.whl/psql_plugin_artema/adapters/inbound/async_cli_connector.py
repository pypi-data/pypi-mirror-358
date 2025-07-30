from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Optional, Dict, Any
import pandas as pd
from pydantic import validate_call

from psql_plugin_artema.adapters.outbound.async_psql_port import AsyncPSQLClient
from psql_plugin_artema.application.schemas.psql_connector_service_schemas import ShowTablesParams, GetColumnsParams, \
    AsyncExecuteQueryParams, PSQLConnectorParams
from psql_plugin_artema.application.services.async_connector_service import AsyncPSQLConnectorService

class AsyncPSQLConnector:
    @validate_call()
    def __init__(
            self,
            host: str = 'localhost',
            port: int = 5432,
            database: str = "postgres",
            *,
            user: Optional[str] = None,
            password: Optional[str] = None,
        ):
        self.params = PSQLConnectorParams(
            host=host, port=port, database=database,
            user=user, password=password
        )
        connect_kwargs = self.params.model_dump(exclude_unset=True)
        self._client = AsyncPSQLClient(**connect_kwargs)
        self._service = AsyncPSQLConnectorService(self._client)
        self._txn_conn = None

    async def __aenter__(self):
        await self._client.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._txn_conn:
            await self._txn_conn.execute("ROLLBACK")
            await self._release_txn()
        await self._client.close()

    @asynccontextmanager
    async def transaction(self):
        self._txn_conn = await self._client._pool.acquire()
        try:
            await self._txn_conn.execute("BEGIN")
            yield self
            await self._txn_conn.execute("COMMIT")
        except:
            await self._txn_conn.execute("ROLLBACK")
            raise
        finally:
            await self._release_txn()

    async def _release_txn(self):
        await self._client._pool.release(self._txn_conn)
        self._txn_conn = None

    async def commit(self) -> None:
        """
        Фиксируем текущую транзакцию и сразу же начинаем новую
        на том же соединении.
        """
        assert self._txn_conn, "Нет активной транзакции"
        await self._txn_conn.execute("COMMIT")
        await self._txn_conn.execute("BEGIN")

    async def rollback(self) -> None:
        """
        Откатываем текущую транзакцию и сразу же начинаем новую
        на том же соединении.
        """
        assert self._txn_conn, "Нет активной транзакции"
        await self._txn_conn.execute("ROLLBACK")
        await self._txn_conn.execute("BEGIN")

    async def list_databases(self) -> List[str]:
        return await self._service.list_databases()

    async def list_schemas(self) -> List[str]:
        return await self._service.list_schemas()

    @validate_call
    async def list_tables(self, schema: str = 'public') -> List[str]:
        params = ShowTablesParams(db_schema=schema)
        return await self._service.list_tables(params)

    @validate_call
    async def get_columns(self, schema: str, table: str) -> List[Dict[str, Any]]:
        params = GetColumnsParams(table=table, db_schema=schema)
        return await self._service.get_columns(params)

    @validate_call
    async def execute_query(
        self,
        query: str,
        parameters: Optional[List[Any]] = None,
    ) -> List[Dict[str, Any]]:
        params = AsyncExecuteQueryParams(query=query, parameters=parameters)
        if self._txn_conn:
            stmt = await self._txn_conn.prepare(params.query)
            rows = await stmt.fetch(*(params.parameters or []))
            return [dict(r) for r in rows]
        return await self._service.execute_query(params)

    async def read_table_in_chunks(
        self,
        schema: str, table: str,
        chunk_size: int, order_by: Optional[str] = None
    ) -> AsyncGenerator[pd.DataFrame, None]:
        async for df in self._service.read_table_in_chunks(
            schema=schema,
            table=table,
            chunk_size=chunk_size,
            order_by=order_by
        ):
            yield df
