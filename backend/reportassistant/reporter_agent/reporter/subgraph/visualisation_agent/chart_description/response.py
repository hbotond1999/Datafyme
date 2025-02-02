from pydantic import BaseModel, Field


class ChartDescription(BaseModel):
    """
    ChartDescription:
        A class to store the created chart description.

    Attributes:
        description: The text of the refined SQL query
    """
    description: str = Field(description="The chart description")
