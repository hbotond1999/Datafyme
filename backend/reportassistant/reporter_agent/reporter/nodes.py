from common.db.manager.database_manager import DatabaseManager
from reporter_agent.reporter.agents import create_history_summarizer
from reporter_agent.reporter.state import GraphState
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.graph import create_sql_agent_graph
from reporter_agent.reporter.subgraph.visualisation_agent.ai.graph import create_graph as create_visu_graph


def summarize_history_node(state: GraphState):
    new_question = create_history_summarizer().invoke(
        {"chat_history": state["chat_history"], "question": state["question"]}
    )
    return {"question": new_question}


def create_sql_query_node(state: GraphState):
    result = create_sql_agent_graph().invoke({"message": state["question"], "database_source": state["database_source"]})
    return {"sql_query": result["sql_query"], "sql_query_description": result["query_description"]}


def run_sql_query_node(state: GraphState):
    db_manager = DatabaseManager(state["database_source"])
    try:
        data  = db_manager.execute_sql(state["sql_query"], response_format="list")
        return {"sql_query_result": data, "error_message": None}
    except Exception as e:
        return {"error_message": str(e)}


def create_visualization_node(state: GraphState):
    result = create_visu_graph().invoke({"question": state["question"], "input_data": state["sql_query_result"]})

    return {"representation_data": result["final_data"]}