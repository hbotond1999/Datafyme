from langgraph.constants import START, END
from langgraph.graph import StateGraph

from reporter_agent.sql_statement_creator.ai.nodes import hybrid_search_node
from langchain_core.messages import HumanMessage

from reporter_agent.sql_statement_creator.ai.state import GraphState


def create_graph():
    """
    Creates and compiles a state graph representing the workflow of an SQL generation process.

    Returns:
        Compiled state graph for the SQL generation workflow.
    """
    graph = StateGraph(GraphState)
    graph.add_node("hybrid_search_node", hybrid_search_node)

    graph.add_edge(START, "hybrid_search_node")
    graph.add_edge("hybrid_search_node", END)

    return graph.compile()


if __name__ == '__main__':
    message = "Most frequently ordered product."
    sql_graph = create_graph()
    matching_tables = sql_graph.invoke({"message": message})
    print(matching_tables)
