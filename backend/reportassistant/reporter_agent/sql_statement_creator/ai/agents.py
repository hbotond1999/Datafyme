from langchain_core.prompts import PromptTemplate

from common.ai.model import get_llm_model


def sql_agent():
    """
    Creates a representation agent for sql creation tasks.

    Returns:
        A prompt that is combined with a language model for generating responses based on the prompt template.
    """
    prompt_str = """You are a professional sql command writer. 
    Your task is to write an SQL query that answers the following user message. Message: {message}. 
    You must use the following DDL-s containing the useful data columns. DDLs: {ddls}. 
    The generated query can only use the columns included in the ddls. """

    prompt = PromptTemplate(template=prompt_str, input_variables=["ddls", "message"])

    return prompt | get_llm_model()
