from common.db.manager.database_manager import DatabaseManager
from common.db.manager.handlers.utils.exception import ExecuteQueryError
from reporter_agent.reporter.agents import create_history_summarizer, refine_sql_agent, refine_empty_result_sql_agent
from reporter_agent.reporter.state import GraphState
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.graph import create_sql_agent_graph
from reporter_agent.reporter.subgraph.visualisation_agent.ai.graph import create_graph as create_visu_graph


def summarize_history_node(state: GraphState):
    new_question = create_history_summarizer().invoke(
        {"chat_history": state["chat_history"], "question": state["question"]}
    )
    return {"question": new_question}


def create_sql_query_node(state: GraphState):
    result = create_sql_agent_graph().invoke({"message": state["question"],
                                              "database_source": state["database_source"],
                                              "refine_recursive_limit": 3})

    return {"sql_query": result["sql_query"], "sql_query_description": result["query_description"],
            "table_final_ddls": result["table_final_ddls"]}


def run_sql_query_node(state: GraphState):
    db_manager = DatabaseManager(state["database_source"])
    try:
        data = db_manager.execute_sql(state["sql_query"], response_format="list")
        return {"sql_query_result": data, "error_message": None}
    except ExecuteQueryError as e:
        return {"error_message": {"message": e.message, "original_exception": e.original_exception}}


def refine_sql_query_node(state: GraphState):
    refine_sql_recursive_limit = state["refine_sql_recursive_limit"] - 1

    if refine_sql_recursive_limit >= 0:
        result = refine_sql_agent().invoke({"question": state["question"],
                                            "database": state["database_source"],
                                            "ddls": state["table_final_ddls"],
                                            "sql_query": state["sql_query"],
                                            "error_message": state["error_message"]["message"],
                                            "exception": state["error_message"]["original_exception"]})
        return {"sql_query": result.sql_query, "sql_query_description": result.query_description,
                "refine_sql_recursive_limit": refine_sql_recursive_limit}
    else:
        raise SystemExit("Refine sql recursive limit exceeded")


def refine_empty_result_sql_query_node(state: GraphState):
    refine_empty_result_recursive_limit = state["refine_empty_result_recursive_limit"] - 1

    if refine_empty_result_recursive_limit >= 0:
        result = refine_empty_result_sql_agent().invoke({"question": state["question"],
                                                         "database": state["database_source"],
                                                         "ddls": state["table_final_ddls"],
                                                         "sql_query": state["sql_query"]})
        return {"sql_query": result.sql_query, "sql_query_description": result.query_description,
                "refine_empty_result_recursive_limit": refine_empty_result_recursive_limit}
    else:
        raise SystemExit("Refine empty result sql recursive limit exceeded")


def create_visualization_node(state: GraphState):
    result = create_visu_graph().invoke({"question": state["question"], "input_data": state["sql_query_result"]})

    return {"representation_data": result["final_data"]}
