from typing import TypedDict, Any, Dict, List

from reporter_agent.visualisation_agent.chart import BarChart, PieChart, LineChart, BubbleChart, \
    ScatterChart, HistogramChart


class GraphState(TypedDict):
    """
        GraphState is a TypedDict that describes the state of a graph with various attributes.

        Attributes:
            representation_type: A string representing the type of data representation (e.g., "bar", "line").
            chart_type: A string indicating the type of chart (e.g., "historical", "predictive").
            chart_data: A variable of any type holding the data to be visualized in the chart.
            preview_data: A dictionary where the keys are strings and the values are lists of any type,
                          used for previewing a subset of the chart data.
            question: A string containing a descriptive question or title related to the graph.
    """
    representation_type: str
    chart_type: str
    chart_data: BarChart | PieChart | LineChart | BubbleChart | ScatterChart | HistogramChart
    preview_data: Dict[str, List[Any]]
    question: str