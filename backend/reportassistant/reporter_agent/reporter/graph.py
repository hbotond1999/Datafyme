from langgraph.constants import START, END
from langgraph.graph import StateGraph

from reporter_agent.reporter.nodes import summarize_history_node, create_sql_query_node, run_sql_query_node, \
    create_visualization_node
from reporter_agent.reporter.state import GraphState


def create_reporter_graph():
    graph = StateGraph(GraphState)
    graph.add_node("summarize_history", summarize_history_node)
    graph.add_node("create_sql_query", create_sql_query_node)
    graph.add_node("run_sql_query", run_sql_query_node)
    graph.add_node("create_visualization", create_visualization_node)

    graph.add_edge(START,"summarize_history")
    graph.add_edge("summarize_history","create_sql_query")
    graph.add_edge("create_sql_query", "run_sql_query")
    graph.add_conditional_edges(
        "run_sql_query",
        lambda x: not x["error_message"],
        {True: "create_visualization", False: END}  # TODO: ERROR HANDLING, SQL QUERY REFINE
    )

    graph.add_edge("create_visualization", END)
    return graph.compile()