from langchain_core.prompts import PromptTemplate

from common.ai.model import get_llm_model
from dbloader.services.vector_loader.ai.response import TableDocumentation


def create_doc_agent():
    """
    Initiates a procedure to create a documentation generating agent.

    The procedure sets up a prompt string designed for a systems analyst to document database tables
    from both technical and business perspectives. The prompt string incorporates a template with
    an input variable `table_schema`.

    The process returns a configured prompt and an LLM model capable of producing structured output
    for table documentation.

    :return: A configured prompt and an LLM model with structured output for table documentation.
    """
    prompt_str = "You are a professional systems analyst with expertise in both business and technical information. "\
             "Your task is to document the database tables from both a technical and business perspective. "\
             "Your response should be concise and informative; "\
             "the business section should reflect the language used by real end-users.) \n"\
             "Table Schema: {table_schema}"

    prompt = PromptTemplate(template=prompt_str, input_variables=["table_schema"])

    return prompt | get_llm_model().with_structured_output(TableDocumentation)