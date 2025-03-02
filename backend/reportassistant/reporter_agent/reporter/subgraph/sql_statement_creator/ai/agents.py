from langchain_core.prompts import PromptTemplate

from common.ai.model import get_llm_model
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.response import SQLCommand, NewQuestion, IsRelevant, \
    BasicChat


def sql_agent():
    """
    Creates a sql agent for sql creation tasks.

    Returns:
        A prompt that is combined with a language model for generating responses based on the prompt template.
    """
    prompt_str = """You are a professional sql command writer. 
    Your task is to write an SQL query that answers the following user message. Message: {message}. 
    You must use the following DDL-s containing the useful data columns. DDLs: {ddls}. 
    The generated query can only use the columns included in the ddls. 
    In the generated query you must use schema reference before every table name.
    The source database is {database}. 
    The system time is {systemtime}.
    """

    prompt = PromptTemplate(template=prompt_str, input_variables=["ddls", "message", "database", "systemtime"])

    return prompt | get_llm_model().with_structured_output(SQLCommand)


def refine_user_question_agent():
    prompt_str = """
    Your task is to refine the user question. User question: {message}. 
    The user's request does not match the tables in the database. Please rephrase the user's question in a way that 
    makes it more suitable for vector database-based search and make sure that the content of the original question 
    does not change.
    The system time is {systemtime}.
    """

    prompt = PromptTemplate(template=prompt_str, input_variables=["message", "systemtime"])

    return prompt | get_llm_model().with_structured_output(NewQuestion)


def filter_relevant_question():
    prompt_str = """
    Your task is to decide whether the message sent by the user is a data analysis question that is intended to query 
    information from a database or just a general chat message, greeting, etc.
    User question: {message}. 
    """

    prompt = PromptTemplate(template=prompt_str, input_variables=["message"])

    return prompt | get_llm_model().with_structured_output(IsRelevant)


def basic_chat():
    prompt_str = """
    System: Your are a helpful data analyst, whose task is to answer analytical questions based on the selected 
    data source.
    Data source: {database}.
    User message: {message}.
    """

    prompt = PromptTemplate(template=prompt_str, input_variables=["message", "database"])

    return prompt | get_llm_model().with_structured_output(BasicChat)
