import logging

from common.db.manager.database_manager import DatabaseManager
from common.db.manager.handlers.utils.exception import ExecuteQueryError
from reporter_agent.models import Chart
from reporter_agent.reporter.subgraph.visualisation_agent.chart import ChartTypes, PieChart, BarChart, LineChart, \
    BubbleChart, HistogramChart, ScatterChart, MixedChart, CHART_RESPONSE_MAPPING


def create_chart_data(chart: Chart):
    database_manager = DatabaseManager(chart.data_source)
    try:

        if chart.type == "TABLE":
            data = database_manager.execute_sql(chart.sql_query, "list", row_num=20)
            return data
        else:
            data = database_manager.execute_sql(chart.sql_query, "list")
            chart_class = CHART_RESPONSE_MAPPING.get(chart.type, None)

            if chart_class is None:
                raise ValueError("Unknown chart type: " + str(chart.type))

            return chart_class.create_chart_data(chart, data)
    except ExecuteQueryError as e:
        logging.error(f"Error to get chart data {chart.id} " + e.message)
        raise ExecuteQueryError(e)


def create_chart_meta_data(chart: Chart):
    database_manager = DatabaseManager(chart.data_source)
    try:
        data = database_manager.execute_sql(chart.sql_query, "list")
        return data
    except ExecuteQueryError as e:
        logging.error(f"Error to get chart data {chart.id} " + e.message)
        raise ExecuteQueryError(e)
