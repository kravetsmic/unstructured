# https://developers.notion.com/reference/property-object#number
from dataclasses import dataclass
from typing import Optional

from unstructured.ingest.connector.notion.interfaces import (
    DBCellBase,
    DBPropertyBase,
    FromJSONMixin,
)


@dataclass
class NumberProp(FromJSONMixin):
    format: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class Number(DBPropertyBase):
    id: str
    name: str
    number: NumberProp
    type: str = "number"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(number=NumberProp.from_dict(data.pop("number")), **data)


@dataclass
class NumberCell(DBCellBase):
    id: str
    number: int
    type: str = "number"
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def get_text(self) -> Optional[str]:
        return str(self.number)
