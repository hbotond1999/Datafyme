from pydantic import BaseModel, Field


class BubbleChart(BaseModel):
    X_axis_column_name: str = Field(description="This column represents one variable, which determines the horizontal position of each bubble.This could be a numeric value")
    Y_axis_column_name: str = Field(description="This column represents a second variable, which determines the vertical position of each bubble. This could be another numeric value or any other metric of interest.")
    size_column_name: str = Field(description="The size of each bubble represents a third variable, indicating the value of that variable. The larger the bubble, the greater the value of this third variable. For example, it could be used to show volume, sales, population, or any other quantitative measure.")