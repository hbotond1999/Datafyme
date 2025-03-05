from typing import Optional

from pydantic import BaseModel, Field

from reporter_agent.reporter.subgraph.visualisation_agent.chart.abc import Chart

from reporter_agent.reporter.subgraph.visualisation_agent.chart.utils import axis_date_str_converter


class LineChart(BaseModel, Chart):
    x_axis_column_name: str = Field(description='Represents the independent variable, often time (e.g., days, months, years).')
    y_axis_column_name: str = Field(description='Shows the dependent variable, the value being measured (e.g., temperature, revenue, or population).')
    date_format: Optional[str] = Field(description='The date or date time format to use, to show values of the x_axis_column in the chart. It should be Python compatible.', default=None)

    def create_meta_data(self):
        return {
            "x_axis": self.x_axis_column_name,
            "y_axis": self.y_axis_column_name,
            "date_format": self.date_format,
        }

    @classmethod
    def create_chart_data(cls, chart, data):
        x_axis = chart.meta_data["metadata"]["x_axis"]
        y_axis = chart.meta_data["metadata"]["y_axis"]
        date_format = chart.meta_data["metadata"].get("date_format", None)
        print(date_format)
        if not date_format:
            labels = data[x_axis]
        else:
            labels = axis_date_str_converter(dates=data[x_axis], date_format=date_format)

        return {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": y_axis,
                    "data": data[y_axis],
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "backgroundColor": "rgba(75, 192, 192, 0.4)",
                    "fill": True
                }]
            },
            "options": {
                "maintainAspectRatio": False,
                "scales": {
                    "x": {
                        "beginAtZero": True
                    },
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }
