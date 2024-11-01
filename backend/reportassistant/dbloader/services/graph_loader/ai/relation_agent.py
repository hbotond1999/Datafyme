from langchain_core.prompts import PromptTemplate

from common.ai.model import get_llm_model
from dbloader.services.graph_loader.ai.response import FoundRelations


def find_relation_agent():
    """
    Initiates a procedure to create a relation finder agent.

    The procedure sets up a prompt string designed for a professional database manager to find public key-foreign key
    relations between tables using the given table previews. The prompt string incorporates a template with
    an input variable `table_previews`.

    The process returns a configured prompt and an LLM model capable of producing structured output
    for found relations.

    :return: A configured prompt and an LLM model with structured output for found relations.
    """
    prompt_str = "You are a professional database manager expertise in entity-relation diagrams. "\
                 "Your task is to find public key-foreign key relations between tables using the given table previews."\
                 "You can only work from the data you received. \n" \
                 "Table previews: {table_previews}"

    prompt = PromptTemplate(template=prompt_str, input_variables=["table_previews"])

    return prompt | get_llm_model().with_structured_output(FoundRelations)
