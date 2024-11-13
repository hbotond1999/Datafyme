from reporter_agent.visualisation_agent.ai.agents import create_representation_agent, create_chart_selector_agent, \
    create_chart_def_agent
from reporter_agent.visualisation_agent.ai.state import GraphState
from reporter_agent.visualisation_agent.chart import CHART_RESPONSE_MAPPING


def decide_representation(state: GraphState):

    result = create_representation_agent().invoke({'preview_data': state["preview_data"]})
    return {"representation_type": result}


def decide_chart_type(state: GraphState):
    result = create_chart_selector_agent().invoke({'preview_data': state["preview_data"]})
    return {"chart_type": result}


def populate_chart_data(state: GraphState):
    result = (create_chart_def_agent(CHART_RESPONSE_MAPPING.get(state["chart_type"]))
              .invoke({"preview_data": state["preview_data"], "chart_type": state["chart_type"]}))
    return {"chart_data": result}