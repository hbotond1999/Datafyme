import logging

from common.db.manager.database_manager import DatabaseManager
from common.db.manager.handlers.utils.exception import ExecuteQueryError
from reporter_agent.models import Chart
from reporter_agent.reporter.subgraph.visualisation_agent.ai import RepType
from reporter_agent.reporter.subgraph.visualisation_agent.chart import ChartTypes, PieChart, BarChart, LineChart, \
    BubbleChart, HistogramChart, ScatterChart


def create_chart_data(chart: Chart):
    database_manager = DatabaseManager(chart.data_source)
    try:
        data = database_manager.execute_sql(chart.sql_query, "list")
        if chart.type == "TABLE":
            return data
        else:
            if chart.type == ChartTypes.PIE.value:
                chart_data = PieChart.create_chart_data(chart, data)
            elif  chart.type == ChartTypes.BAR.value:
                chart_data = BarChart.create_chart_data(chart, data)
            elif chart.type == ChartTypes.LINE.value:
                chart_data = LineChart.create_chart_data(chart, data)
            elif chart.type == ChartTypes.BUBBLE.value:
                chart_data = BubbleChart.create_chart_data(chart, data)
            elif chart.type == ChartTypes.HISTOGRAM.value:
                chart_data = HistogramChart.create_chart_data(chart, data)
            elif chart.type == ChartTypes.SCATTER.value:
                chart_data = ScatterChart.create_chart_data(chart, data)
            else:
                raise ValueError("Unknown chart type")
            return chart_data
    except ExecuteQueryError as e:
        logging.error(f"Error to get chart data {chart.id} " + e.message)
        raise ExecuteQueryError(e)
