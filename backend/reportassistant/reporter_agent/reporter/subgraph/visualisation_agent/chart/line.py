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
