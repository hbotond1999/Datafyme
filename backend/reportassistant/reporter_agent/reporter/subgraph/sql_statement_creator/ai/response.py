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


class NewQuestion(BaseModel):
    """
    NewQuestion:
        A class to store the new user question.

    Attributes:
        message: The text of the original user question
    """
    message: str = Field(description="The refined user question")

