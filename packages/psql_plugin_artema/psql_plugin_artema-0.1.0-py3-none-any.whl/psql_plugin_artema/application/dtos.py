from dataclasses import dataclass
from typing import List, Dict, Any

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict

from psql_plugin_artema.domain.entities import PSQLColumn


# ──────────────────────────   простые коллекции   ────────────────────────── #

@dataclass(slots=True, frozen=True)
class TablesDTO:
    """Список таблиц схемы."""
    tables: List[str]


@dataclass(slots=True, frozen=True)
class DatabasesDTO:
    """Список физических БД на сервере."""
    databases: List[str]


@dataclass(slots=True, frozen=True)
class SchemasDTO:
    """Список схем в текущей БД."""
    schemas: List[str]


# ───────────────────   объекты со структурированными данными   ───────────── #

class ColumnsDTO(BaseModel):
    """Описание колонок конкретной таблицы."""
    columns: List[PSQLColumn]


class RowsDTO(BaseModel):
    """
    Результат произвольного SELECT/INSERT … RETURNING …
    – каждая запись представлена dict’ом «колонка→значение».
    """
    rows: List[Dict[str, Any]]


class ChunkDTO(BaseModel):
    """
    Один фрагмент таблицы, полученный методом read_table_chunk.
    DataFrame также сохранён, чтобы не пересчитывать.
    """
    offset: int
    limit: int
    data: List[Dict[str, Any]]
    dataframe: pd.DataFrame = Field(exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, *, offset: int, limit: int) -> "ChunkDTO":
        return cls(
            offset=offset,
            limit=limit,
            data=df.to_dict(orient="records"),
            dataframe=df,
        )

    def __len__(self) -> int:
        return len(self.data)

class CountDTO(BaseModel):
    """Ответ на SELECT COUNT(*)."""
    count: int = Field(..., ge=0)
