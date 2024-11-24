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