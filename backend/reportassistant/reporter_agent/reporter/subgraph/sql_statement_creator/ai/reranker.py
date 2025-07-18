import logging

from langchain_core.prompts import PromptTemplate

from common.ai.model import get_llm_model
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.response import GradedDDLs, RequiredTableList

logger = logging.getLogger('reportassistant.custom')


def grade_all_ddl():
    prompt_str = """You are a grader assessing relevance of a retrieved table documentations to a user question.\n 
        Here are the retrieved table documentations: \n\n {ddls} \n\n
        Here is the user question: {message} \n
        If a table documentation contains at least one column that is necessary to answer the question given by the user, 
        grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
        Give a binary score "yes" or "no" score to indicate whether the ddl is relevant to the question. \n
        Return the incoming ddls too.
        Provide the binary score as a JSON with a single key 'score' and no premable or explanation."""

    prompt = PromptTemplate(template=prompt_str, input_variables=["message", "ddls"])

    return prompt | get_llm_model().with_structured_output(GradedDDLs)


def table_filter_agent():
    prompt_str = """
You are a grader assessing the relevance of SQL table documentation to a user question.

You will be given: 
- A user question that requires writing an SQL query.
- A list of table documentations (including table names and their column descriptions).

Your task is to identify which tables are relevant to answer the user's question — that is, which tables are needed to construct the correct SQL query.

Return only the relevant tables.

Relevance criteria:
A table is considered relevant if:
 - It contains data directly required to answer the question (e.g., specific fields or attributes mentioned or implied).
 - It is a junction (linking) table that connects relevant entities (e.g., for many-to-many relationships) and is needed to join other relevant tables.
 - It provides foreign keys or references essential for building joins between tables.
 
Do not include tables that are unrelated or not needed for either data or joining purposes.

Here are the retrieved table documentations: \n\n {ddls} \n\n
Here is the user question: {message} \n
    """
    prompt = PromptTemplate(template=prompt_str, input_variables=["message", "ddls"])

    return prompt | get_llm_model().with_structured_output(RequiredTableList)
