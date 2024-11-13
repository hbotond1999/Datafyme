from pydantic import BaseModel, Field


class HistogramChart(BaseModel):
    y_axis_column: str = Field(description="he Y-axis displays the count or frequency of values falling within each bin. The height of each bar represents the number of data points within that bin’s range.")