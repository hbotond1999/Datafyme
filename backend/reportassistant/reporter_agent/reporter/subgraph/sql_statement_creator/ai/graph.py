from langgraph.constants import START, END
from langgraph.graph import StateGraph

from reporter_agent.reporter.subgraph.sql_statement_creator.ai.nodes import hybrid_search_node, get_ddls, reranker, \
    relation_graph, get_final_ddls, create_query, refine_user_question, filter_basic_chat

from reporter_agent.reporter.subgraph.sql_statement_creator.ai.state import GraphState


def create_sql_agent_graph():
    """
    Creates and compiles a state graph representing the workflow of an SQL generation process.

    Returns:
        Compiled state graph for the SQL generation workflow.
    """
    graph = StateGraph(GraphState)
    graph.add_node("filter_basic_chat_node", filter_basic_chat)
    graph.add_node("hybrid_search_node", hybrid_search_node)
    graph.add_node("get_ddls_node", get_ddls)
    graph.add_node("reranker_node", reranker)
    graph.add_node("refine_user_question_node", refine_user_question)
    graph.add_node("relation_graph_node", relation_graph)
    graph.add_node("get_final_ddls_node", get_final_ddls)
    graph.add_node("create_query_node", create_query)

    graph.add_edge(START, "filter_basic_chat_node")
    graph.add_edge("filter_basic_chat_node", "hybrid_search_node")
    graph.add_edge("hybrid_search_node", "get_ddls_node")
    graph.add_edge("get_ddls_node", "reranker_node")
    graph.add_conditional_edges(
        "reranker_node",
        lambda x: not x["filtered_table_ddls"] == [],
        {True: "relation_graph_node", False: "refine_user_question_node"}
    )
    graph.add_edge("refine_user_question_node", "hybrid_search_node")
    graph.add_edge("relation_graph_node", "get_final_ddls_node")
    graph.add_edge("get_final_ddls_node", "create_query_node")
    graph.add_edge("create_query_node", END)

    return graph.compile()
