import asyncio

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from common.ai.model import get_llm_model
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.state import GraphState

prompt = PromptTemplate(
    template="""You are a grader assessing relevance of a retrieved ddl (data definition language) to a user question.\n 
    Here are the retrieved ddl: \n\n {ddl} \n\n
    Here is the user question: {message} \n
    If the DDL contains at least one column that is necessary to answer the question given by the user, 
    grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score "yes" or "no" score to indicate whether the ddl is relevant to the question. \n
    Provide the binary score as a JSON with a single key 'score' and no premable or explanation.""",
    input_variables=["message", "ddl"],
)

retrieval_grader = prompt | get_llm_model() | JsonOutputParser()


async def grade_ddls(state: GraphState):
    """
    Determines whether the ddls are relevant to the question in parallel.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates ddls key with only filtered relevant documents
    """
    message = state["message"]
    ddls = state["matching_table_ddls"]

    # Create a list of tasks for grading each document
    tasks = [grade_ddl(message, ddl) for ddl in ddls]
    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)

    # Filter relevant ddls
    filtered_ddls = [ddl for relevant, ddl in results if relevant]

    return filtered_ddls


async def grade_ddl(message: str, ddl: dict):
    """
    Determines the relevance of a single ddl.

    Args:
        message (str): The question to evaluate against.
        ddl (dict): The ddl to be graded.

    Returns:
        (bool, object): A tuple where the first element indicates if the ddl is relevant.
                        The second element is the ddl itself.
    """
    score = await retrieval_grader.ainvoke({"message": message, "ddl": ddl})
    grade = score["score"]
    if grade == "yes":
        return True, ddl
    else:
        return False, ddl
