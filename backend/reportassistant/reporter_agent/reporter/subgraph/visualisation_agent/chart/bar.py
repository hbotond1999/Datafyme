from pydantic import BaseModel, Field

from reporter_agent.reporter.subgraph.visualisation_agent.chart.abc import Chart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.utils import axis_date_str_converter


class BarChart(BaseModel, Chart):
    category_column_name: str = Field(description="This axis displays the categories or groups being compared. Each bar corresponds to one category, such as different products, countries")
    values_column_name: str = Field(description="This axis represents the numerical values associated with each category. The height (or length, in a horizontal bar chart) of each bar shows the value of that category, such as revenue, population, or any other quantitative metric.")
    date_format: str = Field(description='The date format to use, to show values of the x_axis_column in the chart. It should be Python compatible.', default=None)

    def create_meta_data(self):
        return {
            "x_axis": self.category_column_name,
            "y_axis": self.values_column_name,
            "date_format": self.date_format
        }

    @classmethod
    def create_chart_data(cls, chart, data):
        x_axis = chart.meta_data["metadata"]["x_axis"]
        y_axis = chart.meta_data["metadata"]["y_axis"]
        date_format = chart.meta_data["metadata"].get("date_format")

        if date_format:
            labels = axis_date_str_converter(dates=data[x_axis], date_format=date_format)
        else:
            labels = data[x_axis]
        return {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": y_axis,
                    "data": data[y_axis],
                    "borderWidth": 1
                }]
            },
            "options": {
                "maintainAspectRatio": False,
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }
