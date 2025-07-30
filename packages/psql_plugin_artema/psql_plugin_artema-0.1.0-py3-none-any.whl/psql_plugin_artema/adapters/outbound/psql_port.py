from typing import List, Dict, Any, Optional, Generator

import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor, register_uuid, register_default_json, register_default_jsonb
from shapely import wkb

from psql_plugin_artema.application.dtos import TablesDTO, DatabasesDTO, SchemasDTO, ColumnsDTO, RowsDTO, CountDTO, ChunkDTO
from psql_plugin_artema.application.interfaces.psql_port import IPSQLPort
from psql_plugin_artema.application.schemas.psql_connector_service_schemas import ShowTablesParams, GetColumnsParams, \
    ExecuteQueryParams, ReadOneChunkParams
from psql_plugin_artema.domain.entities import PSQLColumn


class PSQLPort(IPSQLPort):
    def __init__(
        self,
        host: str,
        port: int = 5432,
        user: str = None,
        password: str = None,
        database: str = None,
    ):
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=database,
        )
        register_default_json(self.conn, globally=True)
        register_default_jsonb(self.conn, globally=True)
        register_uuid()


    def _get_cursor(self):
        return self.conn.cursor(cursor_factory=RealDictCursor)

    def list_tables(self, params: ShowTablesParams) -> TablesDTO:
        with self._get_cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_type = 'BASE TABLE';
                """,
                (params.db_schema,)
            )
            tables = [row['table_name'] for row in cursor.fetchall()]
        return TablesDTO(tables=tables)

    def list_databases(self) -> DatabasesDTO:
        with self._get_cursor() as cursor:
            cursor.execute(
                """
                SELECT datname
                FROM pg_database
                WHERE datistemplate = false;
                """
            )
            databases = [row['datname'] for row in cursor.fetchall()]
        return DatabasesDTO(databases=databases)

    def list_schemas(self) -> SchemasDTO:
        with self._get_cursor() as cursor:
            cursor.execute(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name NOT IN ('information_schema', 'pg_catalog');"
            )
            schemas = [row['schema_name'] for row in cursor.fetchall()]
        return SchemasDTO(schemas=schemas)

    def get_columns(self, params: GetColumnsParams) -> ColumnsDTO:
        with self._get_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                  c.column_name,
                  c.data_type,
                  c.column_default,
                  c.is_nullable,
                  pgd.description
                FROM information_schema.columns c
                LEFT JOIN pg_catalog.pg_statio_all_tables st
                  ON c.table_schema = %s
                 AND c.table_name = st.relname
                LEFT JOIN pg_catalog.pg_description pgd
                  ON pgd.objoid = st.relid
                 AND pgd.objsubid = c.ordinal_position
                WHERE c.table_name = %s;
                """,
                (params.db_schema, params.table)
            )
            result: List[PSQLColumn] = []
            for row in cursor.fetchall():
                result.append(
                    PSQLColumn(
                        name=row['column_name'],
                        type=row['data_type'],
                        default_type=row.get('column_default'),
                        comment=row.get('description'),
                        is_nullable=row['is_nullable'],
                    )
                )
        return ColumnsDTO(columns=result)

    def run_query(
        self,
        params: ExecuteQueryParams
    ) -> List[Dict[str, Any]]:
        with self._get_cursor() as cursor:
            cursor.execute(params.query, params.parameters)
            if not cursor.description:
                return RowsDTO(rows=[]).rows
            raw = cursor.fetchall()  # List[dict]
            converted = [self._convert_row_types(r) for r in raw]
        return RowsDTO(rows=converted).rows

    def run_query_in_chunks(
            self,
            params: ExecuteQueryParams
    ) -> Generator[ChunkDTO, None, None]:
        with self.conn.cursor(
                name='exec_query_cursor',
                cursor_factory=RealDictCursor
        ) as cur:
            cur.itersize = params.chunk_size
            cur.execute(params.query, params.parameters or {})
            offset = 0
            while True:
                rows = cur.fetchmany(params.chunk_size)
                if not rows:
                    break
                converted = [self._convert_row_types(r) for r in rows]
                import pandas as pd
                df = pd.DataFrame(converted)
                yield ChunkDTO.from_dataframe(
                    df,
                    offset=offset,
                    limit=params.chunk_size
                )
                offset += params.chunk_size

    def count_rows(self, params: GetColumnsParams) -> CountDTO:
        with self._get_cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) AS cnt FROM {params.db_schema}.{params.table}")
            result = cursor.fetchone()['cnt']
        return CountDTO(count=result)

    def read_table_chunk(
            self,
            table: str,
            limit: int,
            offset: int,
            schema: str,
            order_by: str = 'id'
    ) -> ChunkDTO:
        params = ReadOneChunkParams(
            table=table, limit=limit, offset=offset,
            db_schema=schema, order_by=order_by
        )
        query = sql.SQL(
            "SELECT * FROM {}.{}{} LIMIT %s OFFSET %s"
        ).format(
            sql.Identifier(params.db_schema),
            sql.Identifier(params.table),
            sql.SQL(" ORDER BY {}").format(sql.Identifier(params.order_by))
            if params.order_by
            else sql.SQL("")
        )
        with self._get_cursor() as cursor:
            cursor.execute(query, (params.limit, params.offset))
            rows = cursor.fetchall()
            converted = [self._convert_row_types(r) for r in rows]
            df = pd.DataFrame(converted)
        return ChunkDTO.from_dataframe(df, offset=params.offset, limit=params.limit)

    def is_distributed(self, table: str) -> bool:
        return False

    def close(self) -> None:
        """
        Закрывает соединение с базой.
        """
        try:
            self.conn.close()
        except Exception:
            pass

    def _convert_row_types(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Преобразует типы данных в строке результата.
        """
        out: Dict[str, Any] = {}
        for k, v in row.items():
            if isinstance(v, (bytes, memoryview)):
                try:
                    out[k] = wkb.loads(bytes(v))
                    continue
                except Exception:
                    out[k] = bytes(v)
                    continue
            out[k] = v
        return out

