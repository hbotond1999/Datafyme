from pydantic import BaseModel, Field


class LineChart(BaseModel):
    x_axis_column_name: str = Field(description='Represents the independent variable, often time (e.g., days, months, years).')
    y_axis_column_name: str = Field(description='Shows the dependent variable, the value being measured (e.g., temperature, revenue, or population).')
