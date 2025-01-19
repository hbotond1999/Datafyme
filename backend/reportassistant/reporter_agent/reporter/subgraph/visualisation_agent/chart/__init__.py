from enum import Enum
from typing import Dict

from reporter_agent.reporter.subgraph.visualisation_agent.chart.abc import Chart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.bar import BarChart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.bubble import BubbleChart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.histogram import HistogramChart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.line import LineChart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.mixed_chart import MixedChart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.pie import PieChart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.scatter import ScatterChart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.stacked_bar import StackedBarChart


class ChartTypes(Enum):
    BAR = 'BAR_CHART'
    LINE = 'LINE_CHART'
    BUBBLE = 'BUBBLE_CHART'
    HISTOGRAM = 'HISTOGRAM'
    SCATTER = 'SCATTER_CHART'
    PIE = 'PIE_CHART'
    MIXED_CHART = 'MIXED_CHART'
    STACK_BAR_CHART = 'STACK_BAR_CHART'

CHART_RESPONSE_MAPPING: Dict[str, Chart] = {
    ChartTypes.BAR.value: BarChart,
    ChartTypes.PIE.value: PieChart,
    ChartTypes.LINE.value: LineChart,
    ChartTypes.BUBBLE.value: BubbleChart,
    ChartTypes.SCATTER.value: ScatterChart,
    ChartTypes.HISTOGRAM.value: HistogramChart,
    ChartTypes.MIXED_CHART.value: MixedChart,
    ChartTypes.STACK_BAR_CHART.value: StackedBarChart
}