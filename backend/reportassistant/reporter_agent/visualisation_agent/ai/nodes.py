import json

from reporter_agent.visualisation_agent.ai.agents import create_representation_agent, create_chart_selector_agent, \
    create_chart_def_agent
from reporter_agent.visualisation_agent.ai.state import GraphState
from reporter_agent.visualisation_agent.chart import CHART_RESPONSE_MAPPING


def decide_representation(state: GraphState):
    """
    Args:
        state (GraphState): A dictionary-like object containing the current state of the graph
                            that includes 'preview_data' and 'question'.

    Returns:
        dict: A dictionary containing the 'representation_type' derived from the result of invoking
              the representation agent.
    """
    result = create_representation_agent().invoke({'preview_data': json.dumps(state["preview_data"]), 'question': state["question"]})
    return {"representation_type": result.content}


def decide_chart_type(state: GraphState):
    """
    Args:
        state: A GraphState object containing details about the graph, including 'preview_data' and 'question'.

    Returns:
        A dictionary with the key 'chart_type' and the value being the type of chart determined by the agent.
    """
    result = create_chart_selector_agent().invoke({'preview_data': json.dumps(state["preview_data"]), 'question': state["question"]})
    return {"chart_type": result.content}


def populate_chart_data(state: GraphState):
    """
    Args:
        state (GraphState): A dictionary containing the state information for generating chart data.
    """
    agent = create_chart_def_agent(CHART_RESPONSE_MAPPING[state["chart_type"]])

    result = agent.invoke({"preview_data": json.dumps(state["preview_data"]), "chart_type": state["chart_type"],  'question': state["question"]})
    return {"chart_data": result}