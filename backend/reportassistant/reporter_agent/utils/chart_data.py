import logging

import pandas as pd

from common.db.manager.database_manager import DatabaseManager
from common.db.manager.handlers.utils.exception import ExecuteQueryError
from reporter_agent.models import Chart
from reporter_agent.reporter.subgraph.visualisation_agent.chart import CHART_RESPONSE_MAPPING


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


def create_pptx_chart(chart: Chart, slide, x, y, cx, cy):
    """
    Creates a PowerPoint chart object or table from a Chart object and adds it to the specified slide.

    Args:
        chart: The Chart object containing type, metadata, and SQL query
        slide: The PowerPoint slide to add the chart to
        x: The x-coordinate for the chart position
        y: The y-coordinate for the chart position
        cx: The width of the chart
        cy: The height of the chart

    Returns:
        A PowerPoint chart or table object that has been added to the slide

    Raises:
        ExecuteQueryError: If there's an error executing the SQL query
        ValueError: If the chart type is unknown
    """
    database_manager = DatabaseManager(chart.data_source)
    try:
        if chart.type == "TABLE":
            data = database_manager.execute_sql(chart.sql_query, "list", row_num=500)
            data = pd.DataFrame(data)
            rows, cols = data.shape
            table = slide.shapes.add_table(
                rows + 1,
                cols,
                x, y, cx, cy
            ).table

            for i, column_name in enumerate(data.columns):
                table.cell(0, i).text = str(column_name)
                table.cell(0, i).fill.solid()
                table.cell(0, i).fill.fore_color.rgb = (200, 200, 200)
                table.cell(0, i).text_frame.paragraphs[0].font.bold = True

            for row_idx, row in enumerate(data.itertuples(index=False)):
                for col_idx, value in enumerate(row):
                    table.cell(row_idx + 1, col_idx).text = str(value)

            for row in range(rows + 1):
                for col in range(cols):
                    cell = table.cell(row, col)
                    paragraph = cell.text_frame.paragraphs[0]
                    paragraph.font.size = 10  # Points

            total_width = cx
            for i in range(cols):
                table.columns[i].width = total_width / cols

            return table
        else:
            data = database_manager.execute_sql(chart.sql_query, "list")
            chart_class = CHART_RESPONSE_MAPPING.get(chart.type, None)
            data = pd.DataFrame(data)
            if chart_class is None:
                raise ValueError("Unknown chart type: " + str(chart.type))
            pptx_chart = chart_class.create_pptx_chart(chart, data, slide, x, y, cx, cy)

            return pptx_chart

    except ExecuteQueryError as e:
        logging.error(f"Error getting chart data for chart {chart.id}: {e.message}")
        raise ExecuteQueryError(e)
    except Exception as e:
        logging.error(f"Error creating chart {chart.id}: {str(e)}")
        raise