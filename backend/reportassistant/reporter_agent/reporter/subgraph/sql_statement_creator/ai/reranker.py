import logging

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from common.ai.model import get_llm_model
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.response import GradedDDLs

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
