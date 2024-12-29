from pydantic import BaseModel,Field

from reporter_agent.reporter.subgraph.visualisation_agent.chart.abc import Chart


class ScatterChart(BaseModel, Chart):
    x_axis_column_name: str = Field(description="The X-axis in a scatter chart represents the independent variable or the variable that is presumed to influence the dependent variable on the Y-axis. This is often something measurable, such as time, temperature, age, or any factor that might logically lead to changes in the variable on the Y-axis")
    y_axis_column_name: str = Field(description="he Y-axis represents the dependent variable, the variable that potentially changes in response to variations in the independent variable on the X-axis. It is often the outcome or effect being studied, like sales, test scores, or response time.")

    def create_meta_data(self):
        return {
            "x_axis": self.x_axis_column_name,
            "y_axis": self.y_axis_column_name
        }

    @classmethod
    def create_chart_data(cls, chart, data):
        x_axis = chart.meta_data["metadata"]["x_axis"]
        y_axis = chart.meta_data["metadata"]["y_axis"]

        new_data = [{"x": x, "y": y} for x, y in zip(data[x_axis], data[y_axis])]

        return {
            "type": "scatter",
            "data": {
                "datasets": [{
                    "label": y_axis,
                    "data": new_data,
                    "backgroundColor": "rgba(255, 99, 132, 0.6)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 1
                }]
            },
            "options": {
                "maintainAspectRatio": False,
            }
        }
