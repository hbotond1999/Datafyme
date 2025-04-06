import json
import logging
import os
from datetime import datetime

from common.custom_logging import log
from common.db.manager.database_manager import DatabaseManager
from common.db.manager.handlers.utils.exception import ExecuteQueryError
from reporter_agent.reporter.agents import create_history_summarizer, refine_sql_agent, refine_empty_result_sql_agent, \
    task_router, q_and_a_agent, seconder_task_router, filter_relevant_question, basic_chat
from reporter_agent.reporter.response import RefinedSQLCommand, IsRelevant, BasicChat
from reporter_agent.reporter.state import GraphState
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.graph import create_sql_agent_graph
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.utils import RefineLimitExceededError
from reporter_agent.reporter.subgraph.visualisation_agent.ai import FinalData, RepType
from reporter_agent.reporter.subgraph.visualisation_agent.ai.graph import create_graph as create_visu_graph
from reporter_agent.reporter.utils import save_graph_png

logger = logging.getLogger('reportassistant.custom')


@log(my_logger=logger)
def filter_basic_chat(state: GraphState):
    """
    Args:
        state (GraphState): A dictionary-like object containing the current state of the graph.

    Returns:
        dict: A dictionary containing the 'message' which is the original user input.
    """
    logger.info("Running filter_basic_chat node: checking if the message is relevant for a reporting tasks.")
    result: IsRelevant = filter_relevant_question().invoke({'message': state["question"]})

    if result.is_relevant:
        logger.info(f"Relevant message for a reporting tasks")
        return {'question': state["question"]}
    else:
        logger.info(f"User message is not relevant for a reporting tasks")
        answer: BasicChat = basic_chat().invoke({'message': state["question"],
                                                 'database': state["database_source"].name})
        raise RefineLimitExceededError(answer.answer)


@log(my_logger=logger)
def task_router_node(state: GraphState):
    result = task_router(question=state["question"], chat_data=state["chat_history"])
    logger.info(f"SQL is needed? {result.is_sql_needed}")
    return {"is_sql_needed": result.is_sql_needed}


@log(my_logger=logger)
def seconder_task_router_node(state: GraphState):
    result = seconder_task_router(question=state["question"], chat_data=state["chat_history"])
    logger.info(f"New chart generation is needed? {result.new_chart_needed}")
    return {"new_chart_needed": result.new_chart_needed}


@log(my_logger=logger)
def summarize_history_node(state: GraphState):
    new_question = create_history_summarizer(question=state["question"], chat_data=state["chat_history"])

    return {"question": new_question}


@log(my_logger=logger)
def create_sql_query_node(state: GraphState):
    sql_agent_graph = create_sql_agent_graph()
    # save graph image:
    if int(os.getenv('DEBUG')) == 1:
        save_graph_png(sql_agent_graph, name='sql_agent_graph')
    logger.info(f"message: {state["question"]}")
    result = sql_agent_graph.invoke({"message": state["question"],
                                     "database_source": state["database_source"],
                                     "language": state["language"],
                                     "refine_recursive_limit": 3})

    return {"sql_query": result["sql_query"], "sql_query_description": result["query_description"],
            "table_final_ddls": result["table_final_ddls"]}


@log(my_logger=logger)
def run_sql_query_node(state: GraphState):
    db_manager = DatabaseManager(state["database_source"])
    try:
        data = db_manager.execute_sql(state["sql_query"], response_format="list", row_num=100)
        return {"sql_query_result": data, "error_message": None}
    except ExecuteQueryError as e:
        return {"error_message": {"message": e.message, "original_exception": e.original_exception}}


@log(my_logger=logger)
def refine_sql_query_node(state: GraphState):
    refine_sql_recursive_limit = state["refine_sql_recursive_limit"] - 1
    logger.info(f"Actual REFINE SQL RECURSIVE LIMIT value: {state["refine_sql_recursive_limit"]}")

    if refine_sql_recursive_limit >= 0:
        result = refine_sql_agent().invoke({"question": state["question"],
                                            "database": state["database_source"],
                                            "ddls": state["table_final_ddls"],
                                            "sql_query": state["sql_query"],
                                            "error_message": state["error_message"]["message"],
                                            "exception": state["error_message"]["original_exception"],
                                            'systemtime': datetime.now().isoformat()})
        return {"sql_query": result.sql_query, "sql_query_description": result.query_description,
                "refine_sql_recursive_limit": refine_sql_recursive_limit}
    else:
        logger.error("Refine sql query recursive limit exceeded")
        raise RefineLimitExceededError("We cannot find the correct query for your question, please rephrase the "
                                       "question or try a different source.")


@log(my_logger=logger)
def refine_empty_result_sql_query_node(state: GraphState):
    refine_empty_result_recursive_limit = state["refine_empty_result_recursive_limit"] - 1
    logger.info(f"Current EMPTY RESULT REFINE RECURSIVE LIMIT value: {refine_empty_result_recursive_limit}")

    if refine_empty_result_recursive_limit >= 0:
        output = refine_empty_result_sql_agent(state["database_source"]).invoke({"sql_query": state["sql_query"]},
                                                                                return_only_outputs=True)
        output_text = output['output']
        json_str = output_text.split("```json")[1].split("```")[0].strip()
        result = RefinedSQLCommand(**json.loads(json_str))
        return {"sql_query": result.sql_query, "sql_query_description": result.query_description,
                "refine_empty_result_recursive_limit": refine_empty_result_recursive_limit}
    else:
        logger.error("Refine empty result sql recursive limit exceeded")
        raise RefineLimitExceededError("We cannot find any data for your question, please rephrase the "
                                       "question or try a different source.")


@log(my_logger=logger)
def create_visualization_node(state: GraphState):
    visu_graph = create_visu_graph()
    # save graph image:
    if int(os.getenv('DEBUG')) == 1:
        save_graph_png(visu_graph, name='visu_graph')
    result = visu_graph.invoke({
        "question": state["question"],
        "input_data": state["sql_query_result"],
        "language": state["language"],
        "error_messages": []}
    )
    return {"representation_data": result["final_data"]}


@log(my_logger=logger)
def create_q_and_a_node(state: GraphState):

    result = q_and_a_agent(state["question"], state["chat_history"])
    final_data = FinalData(type=RepType.TEXT, chart_type=None, data=result, chart_title=None)
    return {"representation_data": final_data}
