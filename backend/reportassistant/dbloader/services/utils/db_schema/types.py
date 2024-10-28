import dataclasses
from dataclasses import dataclass
from typing import List

@dataclass
class Column:
    name: str
    data_type: str
    nullable: bool

@dataclass
class TableSchema:
    name: str
    schema: str
    columns: List[Column]

    def to_dict(self):
        return dataclasses.asdict(self)