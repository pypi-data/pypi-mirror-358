from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class ShowTablesParams(BaseModel):
    db_schema: str = Field(default='public', min_length=1)


class GetColumnsParams(BaseModel):
    table: str = Field(..., min_length=1, )
    db_schema: str = Field(default='public', min_length=1)


class ExecuteQueryParams(BaseModel):
    query: str
    parameters: Optional[Dict[str, Any]] = None
    chunk_size: Optional[int] = None

#Появилось необходимость изменить схему ExecuteQueryParams, так как asyncpg не принимает именованные аргументы
class AsyncExecuteQueryParams(BaseModel):
    query: str = Field(..., min_length=1)
    parameters: Optional[List[Any]] = None


class ReadChunksParams(BaseModel):
    table: str = Field(..., min_length=1)
    chunk_size: int = Field(..., gt=0)
    db_schema: str = Field('public', min_length=1)
    order_by: str = Field(
        default='id',
        min_length=1,
    )

class ReadOneChunkParams(BaseModel):
    table: str = Field(..., min_length=1)
    limit: int = Field(..., gt=0)
    offset: int = Field(..., ge=0)
    db_schema: str = Field('public', min_length=1)
    order_by: str = Field(
        default='id',
        min_length=1,
    )


class PSQLConnectorParams(BaseModel):
    host: str = Field(
        default='localhost',
        description="Адрес хоста PostgreSQL"
    )
    port: int = Field(
        default=5432,
        gt=0,
        lt=65536,
        description="Порт сервера (1–65535)"
    )
    database: str = Field(
        default='postgres',
        description="Имя базы данных"
    )
    user: Optional[str] = Field(
        default=None,
        description="Имя пользователя (если нужно)"
    )
    password: Optional[str] = Field(
        default=None,
        description="Пароль (если нужно)"
    )