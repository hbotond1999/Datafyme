import json

from common.custom_logging import log
from reporter_agent.reporter.agents import logger
from reporter_agent.reporter.subgraph.visualisation_agent.ai import FinalData, RepType
from reporter_agent.reporter.subgraph.visualisation_agent.ai.agents import create_representation_agent, create_chart_selector_agent, \
    create_chart_def_agent, create_summarize_agent
from reporter_agent.reporter.subgraph.visualisation_agent.ai.state import GraphState
from reporter_agent.reporter.subgraph.visualisation_agent.ai.utils import get_first_ten_records
from reporter_agent.reporter.subgraph.visualisation_agent.chart import CHART_RESPONSE_MAPPING, ChartTypes


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
    preview_data = get_first_ten_records(data=state["input_data"])
    result = create_chart_selector_agent().invoke({'preview_data': json.dumps(preview_data), 'question': state["question"]})
    return {"chart_type": result.content}


@log(my_logger=logger)
def populate_chart_data(state: GraphState):
    """
    Args:
        state (GraphState): A dictionary containing the state information for generating chart data.
    """
    agent = create_chart_def_agent(CHART_RESPONSE_MAPPING[state["chart_type"]])
    preview_data = get_first_ten_records(data=state["input_data"])
    result = agent.invoke({"preview_data": json.dumps(preview_data), "chart_type": state["chart_type"],  'question': state["question"], 'language': state["language"]})
    return {"chart_column_data": result}


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
