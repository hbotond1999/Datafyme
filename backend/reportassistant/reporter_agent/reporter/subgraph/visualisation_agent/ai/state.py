from typing import TypedDict, Any, Dict, List

from reporter_agent.reporter.subgraph.visualisation_agent.ai import FinalData
from reporter_agent.reporter.subgraph.visualisation_agent.chart.abc import Chart


class GraphState(TypedDict):
    """
        GraphState is a TypedDict that describes the state of a graph with various attributes.

        Attributes:
            representation_type: A string representing the type of data representation (e.g., "bar", "line").
            chart_type: A string indicating the type of chart (e.g., "historical", "predictive").
            chart_column_data:
            input_data: A dictionary where the keys are strings and the values are lists of any type.
            question: A string containing a descriptive question or title related to the graph.
    """
    representation_type: str # local
    chart_type: str # local
    chart_column_data: Chart
    input_data: Dict[str, List[Any]] # input
    question: str # input
    language: str
    final_data: FinalData # output