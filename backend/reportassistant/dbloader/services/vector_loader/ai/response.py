from typing import List

from pydantic import BaseModel, Field


class TableColDocumentation(BaseModel):
    """
        Class to hold documentation details for a table column.

        Attributes
        ----------
        name : str
            Name of the column
        type : str
            Type of the column
        description : str
            Detailed description and purpose of the column
    """
    name: str = Field(description="Name of the column")
    type: str = Field(description="Type of the column")
    description: str = Field(description="Detailed description and purpose of the column")

class TableDocumentation(BaseModel):
    """
    TableDocumentation:
        A class to document the schema and pertinent details of a database table.

    Attributes:
        database_name: Name of the database (default is None).
        table_name: Name of the table with the schema.
        schema_name: Name of the schema.
        table_description: Overview of the table and its purpose.
        columns: List of column documentation for the table.
        use_cases: Potential use cases for the table.
        common_queries: Common business queries or questions for the table.
    """
    database_name: str = Field(description="Name of the database", default=None)
    table_name: str = Field(description="Name of the table with the schema")
    schema_name: str = Field(description="Name of the schema")
    table_description: str = Field(description="Overview of the table and its purpose")
    columns: List[TableColDocumentation]
    use_cases: List[str] = Field(description="Potential use cases for the table")
    common_queries: List[str] = Field(description="Common business queries, questions for the table")

