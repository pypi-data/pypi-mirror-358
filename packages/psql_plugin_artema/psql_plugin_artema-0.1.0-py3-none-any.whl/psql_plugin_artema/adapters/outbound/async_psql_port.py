import asyncpg
import pandas as pd
from typing import List, Dict, Any, Optional
from psql_plugin_artema.application.interfaces.async_psql_port import IAsyncPSQLPort
from psql_plugin_artema.application.schemas.psql_connector_service_schemas import ShowTablesParams, GetColumnsParams, \
    AsyncExecuteQueryParams


class AsyncPSQLClient(IAsyncPSQLPort):
    def __init__(self, **connect_kwargs):
        self._connect_kwargs = connect_kwargs
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        self._pool = await asyncpg.create_pool(**self._connect_kwargs)

    async def list_databases(self) -> List[str]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false;")
            return [r["datname"] for r in rows]

    async def list_schemas(self) -> List[str]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name NOT IN ('information_schema','pg_catalog');"
            )
            return [r["schema_name"] for r in rows]

    async def list_tables(self, params: ShowTablesParams) -> List[str]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema=$1 AND table_type='BASE TABLE';",
                params.db_schema
            )
            return [r["table_name"] for r in rows]

    async def get_columns(self, params: GetColumnsParams) -> List[Dict[str, Any]]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT column_name, data_type
                   FROM information_schema.columns
                   WHERE table_schema=$1 AND table_name=$2
                   ORDER BY ordinal_position;""",
                params.db_schema, params.table
            )
            return [{"name": r["column_name"], "type": r["data_type"]} for r in rows]

    async def execute_query(
        self,
        params: AsyncExecuteQueryParams
    ) -> List[Dict[str, Any]]:
        async with self._pool.acquire() as conn:
            stmt = await conn.prepare(params.query)
            rows = await stmt.fetch(*(params.parameters or []))
            return [dict(r) for r in rows]

    async def read_table_chunk(
        self, schema: str, table: str,
        limit: int, offset: int,
        order_by: Optional[str]
    ) -> pd.DataFrame:
        order = f"ORDER BY {order_by}" if order_by else ""
        sql = f"SELECT * FROM {schema}.{table} {order} LIMIT $1 OFFSET $2"
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, limit, offset)
            return pd.DataFrame([dict(r) for r in rows])

    async def count_rows(self, params: GetColumnsParams) -> int:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT COUNT(*) AS cnt FROM {params.db_schema}.{params.table}"
            )
            return row["cnt"]

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
