from pydantic import BaseModel, Field


class RefinedSQLCommand(BaseModel):
    """
    RefinedSQLCommand:
        A class to store the created SQL commands.

    Attributes:
        sql_query: The text of the refined SQL query
        query_description: The refined SQL query description
    """
    sql_query: str = Field(description="The text of the refined SQL query")
    query_description: str = Field(description="The refined SQL query description")


class IsSQLNeeded(BaseModel):
    is_sql_needed: bool = Field(description="Is it necessary to run a new sql query or not?")