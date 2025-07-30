from typing import Dict, Any, List, Generator, Union

from pydantic import validate_call

from psql_plugin_artema.application.dtos import ChunkDTO
from psql_plugin_artema.application.interfaces.psql_port import IPSQLPort
from psql_plugin_artema.application.schemas.psql_connector_service_schemas import ShowTablesParams, GetColumnsParams, \
    ExecuteQueryParams, ReadChunksParams

class PSQLConnectorService:
    def __init__(self, psql_port: IPSQLPort):
        self.client: IPSQLPort = psql_port

    @validate_call
    def show_tables(self, params: ShowTablesParams):
        return self.client.list_tables(params)

    @validate_call
    def get_columns(self, params: GetColumnsParams):
        return self.client.get_columns(params)

    @validate_call
    def count_rows(self, params: GetColumnsParams):
        return self.client.count_rows(params)

    def list_databases(self):
        return self.client.list_databases()

    def list_schemas(self):
        return self.client.list_schemas()

    @validate_call
    def execute_query(
            self,
            params: ExecuteQueryParams
    ) -> Union[List[Dict[str, Any]], Generator[ChunkDTO, None, None]]:
        stmt = params.query.strip().lower()
        is_select = stmt.startswith('select') or stmt.startswith('with')
        if is_select and params.chunk_size:
            return self.client.run_query_in_chunks(params)
        return self.client.run_query(params)

    @validate_call
    def read_table_in_chunks(
            self,
            params: ReadChunksParams
    ) -> Generator[ChunkDTO, None, None]:
        offset = 0
        while True:
            chunk: ChunkDTO = self.client.read_table_chunk(
                params.table, limit=params.chunk_size, offset=offset,
                schema=params.db_schema, order_by=params.order_by
            )
            if chunk.dataframe.empty:
                break
            yield chunk
            offset += params.chunk_size

