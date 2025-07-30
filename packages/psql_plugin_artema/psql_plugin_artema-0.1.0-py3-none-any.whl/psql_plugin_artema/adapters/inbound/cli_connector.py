from contextlib import contextmanager
from typing import Generator, List, Optional, Dict, Any

from pydantic import validate_call

from psql_plugin_artema.adapters.outbound.psql_port import PSQLPort
from psql_plugin_artema.application.dtos import ChunkDTO
from psql_plugin_artema.application.schemas.psql_connector_service_schemas import (
    ShowTablesParams, GetColumnsParams, ExecuteQueryParams, PSQLConnectorParams, ReadChunksParams
)
from psql_plugin_artema.application.services.connector_service import PSQLConnectorService

class PSQLConnector:
    """
    Синхронный фасад для внешнего мира. Управляет жизненным циклом соединения
    и даёт контекстный менеджер для транзакций.
    """
    @validate_call
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 5432,
        database: str = "postgres",
        *,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.params = PSQLConnectorParams(
            host=host, port=port, database=database,
            user=user, password=password
        )
        self.db = self.params.database
        self._adapter = PSQLPort(
            **self.params.model_dump(exclude_unset=True)
        )
        self._service = PSQLConnectorService(self._adapter)
        self._in_transaction = False

    def __enter__(self) -> "PSQLConnector":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def get_databases(self) -> List[str]:
        return self._service.list_databases()

    def get_schemas(self) -> List[str]:
        return self._service.list_schemas()

    @validate_call
    def get_tables(self, schema: str = 'public') -> List[str]:
        params = ShowTablesParams(db_schema=schema)
        return self._service.show_tables(params)

    @validate_call
    def get_columns(self, table: str, schema: str = 'public'):
        params = GetColumnsParams(table=table, db_schema=schema)
        return self._service.get_columns(params)

    @validate_call
    def count_rows(self, table: str, schema: str = 'public'):
        params = GetColumnsParams(table=table, db_schema=schema)
        return self._service.count_rows(params)

    @validate_call
    def read_table_in_chunks(
        self,
        table: str,
        chunk_size: int,
        schema: str = 'public',
        order_by: str = 'id',
    ) -> Generator[ChunkDTO, None, None]:
        params = ReadChunksParams(table=table, chunk_size=chunk_size, db_schema=schema, order_by=order_by)
        return self._service.read_table_in_chunks(
            params
        )

    @validate_call
    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        chunk_size: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        params = ExecuteQueryParams(query=query, parameters=parameters, chunk_size=chunk_size)
        is_write_operation = query.strip().lower().startswith(
            ('insert', 'update', 'delete', 'create', 'alter', 'drop')
        )
        try:
            result = self._service.execute_query(params)
            if is_write_operation and not self._in_transaction:
                self._adapter.conn.commit()
            return result
        except Exception as e:
            if is_write_operation and not self._in_transaction:
                self._adapter.conn.rollback()
            raise

    @contextmanager
    def transaction(self):
        """
        Контекстный менеджер для ручного управления транзакциями.
        Автоматически обрабатывает коммит/откат и управляет флагом транзакции.
        """
        if self._in_transaction:
            yield self
            return

        self._in_transaction = True
        try:
            yield self
            self._adapter.conn.commit()
        except Exception:
            self._adapter.conn.rollback()
            raise
        finally:
            self._in_transaction = False
            if not self._adapter.conn.closed:
                self._adapter.conn.reset()

    def close(self) -> None:
        if not self._in_transaction and not self._adapter.conn.closed:
            try:
                self._adapter.conn.commit()
            except Exception:
                self._adapter.conn.rollback()
        self._adapter.close()
