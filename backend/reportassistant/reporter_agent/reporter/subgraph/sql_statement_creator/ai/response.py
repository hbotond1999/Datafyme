from typing import List, Dict, Any

from pydantic import BaseModel, Field

from db_configurator.models import TableDocumentation


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


class IsRelevant(BaseModel):
    """
    IsRelevant:
        A class to store true values if the user message is relevant for a data analysis task

    Attributes:
        is_relevant: The text of the original user question
    """
    is_relevant: bool = Field(description="The user message is relevant for a data analysis task")


class BasicChat(BaseModel):

    answer: str = Field(description="The answer for the user message")


class DDLGrade(BaseModel):
    grade: bool = Field(description="The retrieved table documentation is relevant for the user question")
    ddl: List[Dict[str, Any]] = Field(description="The retrieved table documentation")


class GradedDDLs(BaseModel):
    grades: List[bool] = Field(description="The grades of the retrieved table documentations")
    # grades: List[DDLGrade] = Field(description="The grades of the retrieved table documentations")
