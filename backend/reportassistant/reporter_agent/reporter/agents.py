from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate, PromptTemplate

from common.ai.model import get_llm_model
from reporter_agent.reporter.response import RefinedSQLCommand


def create_history_summarizer():
    contextualize_q_system_prompt = """
        Given a chat history and the latest user question which might reference context in the chat history, 
        formulate a standalone question which can be understood without the chat history. Do NOT answer the question, 
        just reformulate it if needed and otherwise return it as is."""

    contextualize_q_human_prompt = """ 
    Question: {question}
    
    (Reminder Do NOT answer the question, just reformulate it if needed and otherwise return it as is.)
    
    """
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", contextualize_q_human_prompt),
        ]
    )

    return contextualize_q_prompt | get_llm_model() | StrOutputParser()


def refine_sql_agent():
    """
    Creates a refine agent for sql refine tasks.

    Returns:
        A prompt that is combined with a language model for generating responses based on the prompt template.
    """
    prompt_str = """You are a professional SQL command refiner.
    Your task is to rewrite an SQL query that responds to the following user question. Question: {question}.
    The faulty SQL query is: {sql_query}.
    The error message you get when running the SQL is: {error_message}.
    The error exception is: {exception}.
    You can still only use the following DDLs to rewrite the SQL (these are the ones that contain the useful data 
    columns). DDLs: {ddls}.
    The source database is: {database}.
    Try to fix and refine the error in the SQL."""

    prompt = PromptTemplate(template=prompt_str, input_variables=["question", "database", "sql_query", "ddls",
                                                                  "error_message", "exception"])

    return prompt | get_llm_model().with_structured_output(RefinedSQLCommand)


def refine_empty_result_sql_agent():
    """
    Creates a refine agent for sql refine tasks.

    Returns:
        A prompt that is combined with a language model for generating responses based on the prompt template.
    """
    prompt_str = """You are a professional SQL command refiner.
    Your task is to rewrite an SQL query that responds to the following user question. Question: {question}.
    The faulty SQL query is: {sql_query}.
    The query syntax is correct, but running the query returns an empty result, so one of the filters is not being used 
    correctly. You can still only use the following DDLs to rewrite the SQL (these are the ones that contain the useful 
    data columns). DDLs: {ddls}.
    The source database is: {database}.
    Try refining the query so that it does not return an empty result."""

    prompt = PromptTemplate(template=prompt_str, input_variables=["question", "database", "sql_query", "ddls"])

    return prompt | get_llm_model().with_structured_output(RefinedSQLCommand)


def generate_title_agent():

    prompt_str = """
    Generate a title for the conversation based on the first message from the user.
    
    First message: {first_message}
    """

    prompt = PromptTemplate(template=prompt_str, input_variables=["first_message"])

    return prompt | get_llm_model() | StrOutputParser()