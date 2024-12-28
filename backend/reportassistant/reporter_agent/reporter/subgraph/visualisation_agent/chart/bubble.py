from pydantic import BaseModel, Field

from reporter_agent.reporter.subgraph.visualisation_agent.chart.abc import Chart


class BubbleChart(BaseModel, Chart):
    X_axis_column_name: str = Field(description="This column represents one variable, which determines the horizontal position of each bubble.This could be a numeric value")
    Y_axis_column_name: str = Field(description="This column represents a second variable, which determines the vertical position of each bubble. This could be another numeric value or any other metric of interest.")
    size_column_name: str = Field(description="The size of each bubble represents a third variable, indicating the value of that variable. The larger the bubble, the greater the value of this third variable. For example, it could be used to show volume, sales, population, or any other quantitative measure.")

    def create_meta_data(self):
        return {
            "x_axis": self.X_axis_column_name,
            "y_axis": self.Y_axis_column_name,
            "size": self.size_column_name
        }

    @classmethod
    def create_chart_data(cls, chart, data):
        x_axis = chart.meta_data["metadata"]["x_axis"]
        y_axis = chart.meta_data["metadata"]["y_axis"]
        size = chart.meta_data["metadata"]["size"]

        # Create data in the format required for a bubble chart
        new_data = [{"x": x, "y": y, "r": r} for x, y, r in zip(data[x_axis], data[y_axis], data[size])]

        return {
            "type": "bubble",
            "data": {
                "datasets": [{
                    "label": chart.title,
                    "data": new_data,
                    "backgroundColor": "rgba(255, 99, 132, 0.6)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 1
                }]
            },
            "options": {
                "maintainAspectRatio": False,
                "scales": {
                    "x": {
                        "beginAtZero": True
                    },
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }