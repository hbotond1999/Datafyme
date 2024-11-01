from typing import List

from pydantic import BaseModel, Field


class TableRelation(BaseModel):
    """
    TableRelation:
        A class to store the found relation.

    Attributes:
        schema: Name of the schema.
        constraint_name: Name of the found constraint.
        table_name: Name of the table with the schema.
        column_name: Name of the column in relation.
        foreign_table_name: Name of the foreign key's table.
        foreign_column_name: Name of the foreign key column.
    """
    schema: str = Field(description="Name of the schema")
    constraint_name: str = Field(description="Name of the found constraint", default='fk')
    table_name: str = Field(description="Name of the table with the schema")
    column_name: str = Field(description="Name of the column in relation")
    foreign_table_name: str = Field(description="Name of the foreign key's table")
    foreign_column_name: str = Field(description="Name of the foreign key column")


class FoundRelations(BaseModel):
    """
    FoundRelations:
        A class to store all the found TableRelation entities in a list.
    """
    relations: List[TableRelation]
