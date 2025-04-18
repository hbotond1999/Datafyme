from pydantic import BaseModel, Field


class IsRelevant(BaseModel):
    """
    IsRelevant:
        A class to store true values if the user message is a data analysis task or not

    Attributes:
        is_relevant: The user message is a data analysis task
    """
    is_relevant: bool = Field(description="The user message is a data analysis task")


class BasicChat(BaseModel):

    answer: str = Field(description="The answer for the user message")


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


class NewChartNeeded(BaseModel):
    new_chart_needed: bool = Field(description="Is it necessary to create new visualizations or not?")
