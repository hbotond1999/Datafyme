from pydantic import BaseModel, Field


class PieChart(BaseModel):
    category_column_name: str = Field(description="This axis displays the categories or groups being compared. Each slice  corresponds to one category, such as different products, countries")
    values_column_name: str = Field(description="This axis represents the numerical values associated with each category")