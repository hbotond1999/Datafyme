from langgraph.constants import START, END
from langgraph.graph import StateGraph

from reporter_agent.sql_statement_creator.ai.nodes import hybrid_search_node, get_ddls, sync_grade_ddls, relation_graph, \
    get_final_ddls, create_query

from reporter_agent.sql_statement_creator.ai.state import GraphState


def create_sql_agent_graph():
    """
    Creates and compiles a state graph representing the workflow of an SQL generation process.

    Returns:
        Compiled state graph for the SQL generation workflow.
    """
    graph = StateGraph(GraphState)
    graph.add_node("hybrid_search_node", hybrid_search_node)
    graph.add_node("get_ddls_node", get_ddls)
    graph.add_node("grade_ddls_node", sync_grade_ddls)
    graph.add_node("relation_graph_node", relation_graph)
    graph.add_node("get_final_ddls_node", get_final_ddls)
    graph.add_node("create_query_node", create_query)

    graph.add_edge(START, "hybrid_search_node")
    graph.add_edge("hybrid_search_node", "get_ddls_node")
    graph.add_edge("get_ddls_node", "grade_ddls_node")
    graph.add_edge("grade_ddls_node", "relation_graph_node")
    graph.add_edge("relation_graph_node", "get_final_ddls_node")
    graph.add_edge("get_final_ddls_node", "create_query_node")
    graph.add_edge("create_query_node", END)

    return graph.compile()
