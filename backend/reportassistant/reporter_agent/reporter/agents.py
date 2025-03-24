import logging

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate, PromptTemplate
from langchain_core.tools import tool

from common.ai.model import get_llm_model
from common.db.manager.database_manager import DatabaseManager
from reporter_agent.reporter.response import RefinedSQLCommand, IsSQLNeeded
from reporter_agent.reporter.utils import png_to_base64

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


def convert_chat_to_llm_format(base_content, chat_data):
    messages = []

    messages.append({"role": "user", "content": base_content})

    for chat in chat_data:
        messages.append({"role": "user", "content": chat["HUMAN"]})

        if "AI" in chat and chat["AI"]:
            ai_content = chat["AI"]
            messages.append({"role": "assistant", "content": ai_content})

        if "image" in chat and chat["image"]:
            base64_img = png_to_base64(chat["image"])
            messages.append({"role": "assistant", "content": f"IMAGE: data:image/png;base64,{base64_img}"})

    return messages


def task_router(question, chat_data):
    prompt_str = """You are a task assigning agent whose job is to decide whether the answer to the user's question can 
    be generated from the data from the chat history or whether a new database query is required. If all the necessary 
    data for the answer is not available, a new SQL query is required to generate the data.
    If it's necessary, use the diagrams in the chat history to provide the answer, as the question may be directed to 
    previously created diagrams.
    """ + f""" User question: {question}.""" + f"""Chat history: """

    message = convert_chat_to_llm_format(prompt_str, chat_data)

    return get_llm_model().with_structured_output(IsSQLNeeded).invoke(message)


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