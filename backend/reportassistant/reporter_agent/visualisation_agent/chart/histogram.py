from pydantic import BaseModel, Field

from reporter_agent.visualisation_agent.chart.abc import Chart


class HistogramChart(BaseModel, Chart):
    y_axis_column: str = Field(description="The Y-axis displays the count or frequency of values falling within each bin. The height of each bar represents the number of data points within that bin’s range.")

    def create_meta_data(self):
        return {
            "y_axis": self.y_axis_column
        }