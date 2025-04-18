from langgraph.constants import START, END
from langgraph.graph import StateGraph

from reporter_agent.reporter.nodes import summarize_history_node, create_sql_query_node, run_sql_query_node, \
    create_visualization_node, refine_sql_query_node, refine_empty_result_sql_query_node, task_router_node, \
    create_q_and_a_node, seconder_task_router_node, filter_basic_chat
from reporter_agent.reporter.state import GraphState


def refine_routes(state: GraphState):
    """Complex routing logic"""
    if not state["error_message"]:
        if not state["sql_query_result"]:
            return "empty_result_table"
        else:
            return "continue"
    else:
        return "error_in_query"


def create_reporter_graph():
    graph = StateGraph(GraphState)
    graph.add_node("filter_basic_chat_node", filter_basic_chat)
    graph.add_node("summarize_history", summarize_history_node)
    graph.add_node("task_router", task_router_node)
    graph.add_node("seconder_task_router", seconder_task_router_node)
    graph.add_node("create_sql_query", create_sql_query_node)
    graph.add_node("run_sql_query", run_sql_query_node)
    graph.add_node("refine_sql_query", refine_sql_query_node)
    graph.add_node("refine_empty_result_sql_query", refine_empty_result_sql_query_node)
    graph.add_node("create_visualization", create_visualization_node)
    graph.add_node("q_and_a", create_q_and_a_node)

    graph.add_edge(START, "filter_basic_chat_node")

    graph.add_conditional_edges(
        "filter_basic_chat_node", lambda x: x["question_is_relevant"],
        {True: "summarize_history", False: END})

    graph.add_edge("summarize_history", "task_router")

    graph.add_conditional_edges(
        "task_router", lambda x: x["is_sql_needed"],
        {True: "create_sql_query", False: "seconder_task_router"})

    graph.add_conditional_edges(
        "seconder_task_router", lambda x: x["new_chart_needed"],
        {True: "create_sql_query", False: "q_and_a"})

    graph.add_edge("create_sql_query", "run_sql_query")
    graph.add_edge("refine_sql_query", "run_sql_query")
    graph.add_edge("refine_empty_result_sql_query", "run_sql_query")

    graph.add_conditional_edges(
        "run_sql_query",
        refine_routes,
        {
            "continue": "create_visualization",
            "error_in_query": "refine_sql_query",
            "empty_result_table": "refine_empty_result_sql_query"
        }
    )

    graph.add_edge("create_visualization", END)
    graph.add_edge("q_and_a", END)
    return graph.compile()
