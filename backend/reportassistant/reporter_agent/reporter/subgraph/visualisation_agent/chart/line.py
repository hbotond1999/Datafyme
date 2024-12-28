from pydantic import BaseModel, Field

from reporter_agent.reporter.subgraph.visualisation_agent.chart.abc import Chart


class LineChart(BaseModel, Chart):
    x_axis_column_name: str = Field(description='Represents the independent variable, often time (e.g., days, months, years).')
    y_axis_column_name: str = Field(description='Shows the dependent variable, the value being measured (e.g., temperature, revenue, or population).')

    def create_meta_data(self):
        return {
            "x_axis": self.x_axis_column_name,
            "y_axis": self.y_axis_column_name
        }

    @classmethod
    def create_chart_data(cls, chart, data):
        x_axis = chart.meta_data["metadata"]["x_axis"]
        y_axis = chart.meta_data["metadata"]["y_axis"]

        return {
            "type": "line",
            "data": {
                "labels": data[x_axis],
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
