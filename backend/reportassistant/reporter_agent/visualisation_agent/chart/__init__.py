from enum import Enum
from types import UnionType

from reporter_agent.visualisation_agent.chart.bar import BarChart
from reporter_agent.visualisation_agent.chart.bubble import BubbleChart
from reporter_agent.visualisation_agent.chart.histogram import HistogramChart
from reporter_agent.visualisation_agent.chart.line import LineChart
from reporter_agent.visualisation_agent.chart.pie import PieChart
from reporter_agent.visualisation_agent.chart.scatter import ScatterChart


class ChartTypes(Enum):
    BAR = 'BAR_CHART'
    LINE = 'LINE_CHART'
    BUBBLE = 'BUBBLE_CHART'
    HISTOGRAM = 'HISTOGRAM'
    SCATTER = 'SCATTER_CHART'
    PIE = 'PIE_CHART'


CHART_RESPONSE_MAPPING = {
    ChartTypes.BAR.value: BarChart,
    ChartTypes.PIE.value: PieChart,
    ChartTypes.LINE.value: LineChart,
    ChartTypes.BUBBLE.value: BubbleChart,
    ChartTypes.SCATTER.value: ScatterChart,
    ChartTypes.HISTOGRAM.value: HistogramChart
}