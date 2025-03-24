from langgraph.constants import START, END
from langgraph.graph import StateGraph

from reporter_agent.reporter.nodes import summarize_history_node, create_sql_query_node, run_sql_query_node, \
    create_visualization_node, refine_sql_query_node, refine_empty_result_sql_query_node, task_router_node
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


def sql_route(state: GraphState):
    """Complex routing logic"""
    if state["is_sql_needed"]:
        return "summarize_history"
    else:
        return "END"


def create_reporter_graph():
    graph = StateGraph(GraphState)
    graph.add_node("task_router", task_router_node)
    graph.add_node("summarize_history", summarize_history_node)
    graph.add_node("create_sql_query", create_sql_query_node)
    graph.add_node("run_sql_query", run_sql_query_node)
    graph.add_node("refine_sql_query", refine_sql_query_node)
    graph.add_node("refine_empty_result_sql_query", refine_empty_result_sql_query_node)
    graph.add_node("create_visualization", create_visualization_node)

    graph.add_edge(START, "task_router")
    graph.add_conditional_edges(
        "task_router",
        sql_route,
        {
            "summarize_history": "summarize_history",
            "END": END
        }
    )
    graph.add_edge("summarize_history", "create_sql_query")
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
    return graph.compile()
