import json
import logging
from datetime import datetime

from django.utils.translation import gettext_noop

from common.custom_logging import log
from reporter_agent.reporter.agents import logger
from reporter_agent.reporter.subgraph.visualisation_agent.ai import FinalData, RepType
from reporter_agent.reporter.subgraph.visualisation_agent.ai.agents import create_representation_agent, \
    create_chart_selector_agent, \
    create_chart_def_agent, create_summarize_agent, create_chart_def_fix_agent
from reporter_agent.reporter.subgraph.visualisation_agent.ai.state import GraphState
from reporter_agent.reporter.subgraph.visualisation_agent.ai.utils import get_first_ten_records
from reporter_agent.reporter.subgraph.visualisation_agent.chart import CHART_RESPONSE_MAPPING, ChartTypes, Chart, \
    BarChart


@log(my_logger=logger)
def decide_representation(state: GraphState):
    """
    Args:
        state (GraphState): A dictionary-like object containing the current state of the graph
                            that includes 'preview_data' and 'question'.

    Returns:
        dict: A dictionary containing the 'representation_type' derived from the result of invoking
              the representation agent.
    """
    if state.get("node_started_callback"):
        state["node_started_callback"]("decide_representation", gettext_noop("Deciding representation type"))
    preview_data = get_first_ten_records(data=state["input_data"])
    result = create_representation_agent().invoke({'preview_data': json.dumps(preview_data), 'question': state["question"]})
    return {"representation_type": result.content}


@log(my_logger=logger)
def decide_chart_type(state: GraphState):
    """
    Args:
        state: A GraphState object containing details about the graph, including 'preview_data' and 'question'.

    Returns:
        A dictionary with the key 'chart_type' and the value being the type of chart determined by the agent.
    """
    if state.get("node_started_callback"):
        state["node_started_callback"]("decide_chart_type", gettext_noop("Deciding chart type"))
    preview_data = get_first_ten_records(data=state["input_data"])
    result = create_chart_selector_agent().invoke({'preview_data': json.dumps(preview_data), 'question': state["question"]})
    return {"chart_type": result.content}


@log(my_logger=logger)
def populate_chart_data(state: GraphState):
    """
    Args:
        state (GraphState): A dictionary containing the state information for generating chart data.
    """
    if state.get("node_started_callback"):
        state["node_started_callback"]("populate_chart_data", gettext_noop("Populating chart data"))
    preview_data = get_first_ten_records(data=state["input_data"])
    if len(state["error_messages"]) > 0 and ["chart_column_data"] is not None:
        agent = create_chart_def_fix_agent(CHART_RESPONSE_MAPPING[state["chart_type"]])
        result = agent.invoke({
            "preview_data": json.dumps(preview_data),
            "chart_type": state["chart_type"],
            "selected_chart_structure": json.dumps(["chart_column_data"]),
            "error_messages": state["error_messages"],
            'language': state["language"]
        })
    else:
        agent = create_chart_def_agent(CHART_RESPONSE_MAPPING[state["chart_type"]])
        result: Chart = agent.invoke({
            "preview_data": json.dumps(preview_data),
            "chart_type": state["chart_type"],
            'question': state["question"],
            'language': state["language"]
        })
    return {"chart_column_data": result}

@log(my_logger=logger)
def validate_chart_data(state: GraphState):
    if state.get("node_started_callback"):
        state["node_started_callback"]("validate_chart_data", gettext_noop("Validating chart data"))
    preview_data = get_first_ten_records(data=state["input_data"])
    error_messages = state["chart_column_data"].validate_chart_data(list(preview_data.keys()))
    return {"error_messages": error_messages}


@log(my_logger=logger)
def create_final_data(state: GraphState):
    """
    Creates the final data based on the state provided.

    Args:
        state: A GraphState object which contains the representation type of the
               data, input data, and other relevant information.

    Returns:
        A dictionary with the key "final_data" mapping to a FinalData object which
        contains type, chart type (if applicable), and the relevant data.
    """
    if state.get("node_started_callback"):
        state["node_started_callback"]("create_final_data", gettext_noop("Creating final data"))
    rep_type = RepType[state["representation_type"]]
    if rep_type == RepType.TEXT:
        response = create_summarize_agent().invoke({"data": state["input_data"], "question": state["question"], "language": state["language"]}).content
        return {
            "final_data": FinalData(type=rep_type, chart_type= None, data=response, chart_title=None)
        }
    elif rep_type == RepType.CHART:
        return {
            "final_data": FinalData(
                type=rep_type,
                chart_type=ChartTypes(state["chart_type"]),
                data={"metadata": state["chart_column_data"].create_meta_data()},
                chart_title=state["chart_column_data"].title)
        }
    else:
        return {"final_data": FinalData(type=rep_type, chart_type=None, data=state["input_data"], chart_title=None)}
