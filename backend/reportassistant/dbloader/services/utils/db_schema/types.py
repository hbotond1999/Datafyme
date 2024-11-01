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


@dataclass
class Relation:
    schema: str
    constraint_name: str
    table_name: str
    column_name: str
    foreign_table_name: str
    foreign_column_name: str


@dataclass
class TablePreview:
    schema: str
    table_name: str
    markdown_preview: str
