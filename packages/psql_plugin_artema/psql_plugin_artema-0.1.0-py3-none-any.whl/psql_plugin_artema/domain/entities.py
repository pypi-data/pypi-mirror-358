from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel


@dataclass(slots=True, frozen=True)
class Column:
    name: str
    type: str


@dataclass(slots=True, frozen=True)
class Table:
    name: str
    columns: List[Column]


class PSQLColumn(BaseModel):
    name: str
    type: str
    default_type: Optional[str] = None
    default_expression: Optional[str] = None
    is_nullable: Optional[bool] = None
    comment: Optional[str] = None
    codec_expression: Optional[str] = None
    ttl_expression: Optional[str] = None