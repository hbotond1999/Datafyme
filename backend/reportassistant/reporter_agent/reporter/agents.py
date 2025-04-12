import logging

import pandas
from django.contrib.postgres.fields import JSONField
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool

from common.ai.model import get_llm_model
from common.db.manager.database_manager import DatabaseManager
from reporter_agent.reporter.response import RefinedSQLCommand, IsSQLNeeded, NewChartNeeded, IsRelevant, BasicChat
from reporter_agent.reporter.utils import png_to_base64

logger = logging.getLogger('reportassistant.custom')


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


def create_history_summarizer(question, chat_data):
    contextualize_q_system_prompt = """
        Given a chat history and a question asked by the user that can refer to the chat history context.
        Write a standalone message that can be understood without the chat history and contains all the information 
        about the original question and the necessary chat history parts. 
        Where possible, reformulate the task into a representation task.
        Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""

    contextualize_q_human_prompt = f""" 
    Question: {question}
    
    (Reminder Do NOT answer the question, just reformulate it if needed and otherwise return it as is.)
    
    """
    base_content = contextualize_q_system_prompt + contextualize_q_human_prompt
    message = convert_chat_to_llm_format(base_content, chat_data)
    human_message = HumanMessage(content=message)

    llm = (get_llm_model() | StrOutputParser())
    return llm.invoke([human_message])


def convert_chat_to_llm_format(base_content, chat_data):
    messages = []

    messages.append({"type": "text", "text": f"{base_content}"})

    for chat in chat_data:
        messages.append({"type": "text", "text": f"HUMAN message: {chat['HUMAN']}"})

        if "AI" in chat and chat["AI"]:
            messages.append({"type": "text", "text": f"AI answer: {chat['AI']}"})

        if "image" in chat and chat["image"]:
            base64_img = png_to_base64(chat["image"])
            messages.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64_img}})

    return messages


def task_router(question, chat_data):
    prompt_str = """You are a task assigning agent whose job is to decide whether the answer to the user's question can 
    be generated from the data from the chat history or whether a new database query is required. If all the necessary 
    data for the answer is not available, a new SQL query is required to generate the data.
    If it's necessary, use the diagrams in the chat history to provide the answer, as the question may be directed to 
    previously created diagrams.
    """ + f"""User question: {question}. Chat history: """

    message = convert_chat_to_llm_format(prompt_str, chat_data)
    human_message = HumanMessage(content=message)
    return get_llm_model().with_structured_output(IsSQLNeeded).invoke([human_message])


def seconder_task_router(question, chat_data):
    prompt_str = """You are a task dispatcher whose job is to decide whether a question asked by a user regarding the 
    content of the chat history requires only a textual answer or whether some visualization needs to be created or 
    modified. 
    If a visualization is not required, but a text-only answer is sufficient, return false.
    If the request requires visualization, return true.
    """ + f"""User question: {question}. Chat history: """

    message = convert_chat_to_llm_format(prompt_str, chat_data)
    human_message = HumanMessage(content=message)
    return get_llm_model().with_structured_output(NewChartNeeded).invoke([human_message])


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
    The system time is {systemtime}.
    
    Try to fix and refine the error in the SQL."""

    prompt = PromptTemplate(template=prompt_str, input_variables=["question", "database", "sql_query", "ddls",
                                                                  "error_message", "exception", "systemtime"])

    return prompt | get_llm_model().with_structured_output(RefinedSQLCommand)


def refine_empty_result_sql_agent(database_source):
    """
    Creates a refine agent for sql refine tasks.

    Returns:
        A prompt that is combined with a language model for generating responses based on the prompt template.
    """

    @tool
    def get_unique_column_values_with_db_manager(table_name: str, column_name: str) -> str:
        """
        Retrieves the unique values of the given column from the given table.

        Args:
            table_name (str): The name of the table with the schema name like: schema_name.table_name.
            column_name (str): The name of the column.

        Returns:
            str: A string containing the unique values of the column.
        """
        db_manager = DatabaseManager(database_source)
        query = f"SELECT DISTINCT {column_name} FROM {table_name}"
        logger.info(f"Refine tool: {query}")
        try:
            unique_values = db_manager.execute_sql(query, response_format="list")
            return f'Unique values in {column_name}: ' + ', '.join(unique_values[column_name])
        except Exception as e:
            logger.error(f"Error fetching unique values for {table_name}.{column_name}: {str(e)}")
            raise RuntimeError(f"Failed to fetch unique values for {table_name}.{column_name}")

    prompt_str = """Your task is to replace the filter value of the sql query with a real value that you can get with 
    the help of the tool. The tool lists the unique values in a given column. 
    Select the appropriate value for filtering and replace it in the input sql.
    Input sql: {sql_query}
    
    Output:
        Provide the result in the following JSON format:
        {{
            "sql_query": "<refined_sql_query>",
            "query_description": "<description_of_the_query>"
        }}
        
    {agent_scratchpad}
    """

    parser = PydanticOutputParser(pydantic_object=RefinedSQLCommand)

    prompt = PromptTemplate(template=prompt_str, input_variables=["sql_query"], output_parser=parser)
    tools = [get_unique_column_values_with_db_manager]
    llm = get_llm_model()

    agent = create_openai_tools_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
    )

    return agent_executor


def generate_title_agent():

    prompt_str = """
    Generate a title for the conversation based on the first message from the user. Formulate the title in this language: {language}.
    
    First message: {first_message}
    """

    prompt = PromptTemplate(template=prompt_str, input_variables=["first_message", "language"])

    return prompt | get_llm_model() | StrOutputParser()


def q_and_a_agent(question, chat_data):
    prompt_str = """
    Based on the input chat history, please answer the question asked by the user.
    """ + f"""User question: {question}. Chat history: """

    message = convert_chat_to_llm_format(prompt_str, chat_data)
    human_message = HumanMessage(content=message)
    llm = (get_llm_model() | StrOutputParser())
    return llm.invoke([human_message])


def dataframe_date_decider():
        prompt_str ="""
## Context
Analyze the provided dataframe and determine the optimal data type for each column. Proper data typing is essential for efficient storage, accurate calculations, and meaningful visualizations.

## Input Dataframe
Dataframe: {dataframe}

## Instructions
Examine EVERY column in the dataframe and classify each into the most appropriate data type:
1. Analyze the content pattern and values
2. Analyze the column name
3. Consider the business context when determining types
4. Identify any data quality issues that might affect typing

## Required Output Format
Return a valid JSON with the following structure:
{{
  "column_types": [
    {{
      "name": "column_name",
      "recommended_type": "one of: string, int, float, date, datetime, bool",
      "parsing_format": "For date/datetime: exact pandas format string (e.g., '%Y-%m-%d') needed for pd.to_datetime()",
    }}
  ]
}}
"""
        prompt = PromptTemplate(template=prompt_str, input_variables=["dataframe"])

        return prompt | get_llm_model() | JsonOutputParser()