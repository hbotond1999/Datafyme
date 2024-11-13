from pydantic import BaseModel, Field


class BarChart(BaseModel):
    category_column_name: str = Field(description="This axis displays the categories or groups being compared. Each bar corresponds to one category, such as different products, countries")
    values_column_name: str = Field(description="This axis represents the numerical values associated with each category. The height (or length, in a horizontal bar chart) of each bar shows the value of that category, such as revenue, population, or any other quantitative metric.")