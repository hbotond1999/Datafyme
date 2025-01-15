import logging

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate, PromptTemplate
from langchain_core.tools import tool

from common.ai.model import get_llm_model
from common.db.manager.database_manager import DatabaseManager
from reporter_agent.reporter.response import RefinedSQLCommand

logger = logging.getLogger('reportassistant.custom')


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

    prompt_str = """You are a professional SQL command refiner.
    Your task is to rewrite an SQL query that responds to the following user question. Question: {input}.
    The faulty SQL query is: {sql_query}.
    The query syntax is correct, but running the query returns an empty result, so one of the filters is not being used 
    correctly. You may be trying to filter by the wrong value. You can use a tool to query the unique values of the 
    columns in the filter.
    You can still only use the following DDLs to rewrite the SQL (these are the ones that contain the useful data 
    columns). DDLs: {ddls}.
    The source database is: {database}.
    The system time is {systemtime}.
    Try refining the query so that it does not return an empty result.
    
    You have to follow the following steps
        1. step: look through the filters to see which columns you are filtering by
        2. step: check if you are filtering on a value that is in the given column. To do this, use the tool which lists 
        the unique values in the column
        3. step: in the query update the filter condition with one of the values from the list given by the tool. 
            Replace the original filter value with one value from the given list.
            The schema name should always appear before the table.
        4. step: Return the refined query. The schema name should always appear before the table.
            Output:
                Provide the result in the following JSON format:
                {{
                    "sql_query": "<refined_sql_query>",
                    "query_description": "<description_of_the_query>"
                }}
        
    {agent_scratchpad}
    """

    parser = PydanticOutputParser(pydantic_object=RefinedSQLCommand)

    prompt = PromptTemplate(template=prompt_str, input_variables=["input", "database", "sql_query", "ddls",
                                                                  "systemtime"], output_parser=parser)
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
