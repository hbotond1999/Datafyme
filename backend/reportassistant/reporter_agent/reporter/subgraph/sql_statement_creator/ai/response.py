from pydantic import BaseModel, Field


class SQLCommand(BaseModel):
    """
    SQLCommand:
        A class to store the created SQL commands.

    Attributes:
        sql_query: The text of the query
        query_description: The query description
    """
    sql_query: str = Field(description="The text of the query")
    query_description: str = Field(description="The query description")
