from typing import List, Dict, Any

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


class DDLGrade(BaseModel):
    grade: bool = Field(description="The retrieved table documentation is relevant for the user question")
    ddl: List[Dict[str, Any]] = Field(description="The retrieved table documentation")


class GradedDDLs(BaseModel):
    grades: List[bool] = Field(description="The grades of the retrieved table documentations")
    # grades: List[DDLGrade] = Field(description="The grades of the retrieved table documentations")


class RequiredTable(BaseModel):
    table_name: str = Field(description="The name of the required table")
    schema: str = Field(description="The schema of the required table")

class RequiredTableList(BaseModel):
    tables: List[RequiredTable] = Field(description="The required tables list")
