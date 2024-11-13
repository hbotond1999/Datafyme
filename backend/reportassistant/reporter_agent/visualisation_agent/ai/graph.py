from langgraph.constants import START, END
from langgraph.graph import StateGraph

from reporter_agent.visualisation_agent.ai import RepType
from reporter_agent.visualisation_agent.ai.nodes import decide_representation, decide_chart_type, populate_chart_data
from reporter_agent.visualisation_agent.ai.state import GraphState


def create_graph():
    """
    Creates and compiles a state graph representing the workflow of a data visualization process.

    Returns:
        Compiled state graph for the data visualization workflow.
    """
    graph = StateGraph(GraphState)
    graph.add_node("decide_representation", decide_representation)
    graph.add_node("decide_chart_type", decide_chart_type)
    graph.add_node("populate_chart_data", populate_chart_data)

    graph.add_edge(START, "decide_representation")
    graph.add_conditional_edges(
        "decide_representation", lambda x: x["representation_type"],
        {RepType.TEXT.value: END,  RepType.CHART.value: "decide_chart_type", RepType.TABLE.value: END})

    graph.add_edge("decide_chart_type", "populate_chart_data")
    graph.add_edge("populate_chart_data", END)

    return graph.compile()
