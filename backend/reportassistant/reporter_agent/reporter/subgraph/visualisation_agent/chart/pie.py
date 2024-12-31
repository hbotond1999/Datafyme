from pydantic import BaseModel, Field

from reporter_agent.reporter.subgraph.visualisation_agent.chart.abc import Chart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.color import ColorPalette


class PieChart(BaseModel, Chart):
    category_column_name: str = Field(description="This axis displays the categories or groups being compared. Each slice  corresponds to one category, such as different products, countries")
    values_column_name: str = Field(description="This axis represents the numerical values associated with each category")

    def create_meta_data(self):
        return {
            "x_axis": self.category_column_name,
            "y_axis": self.values_column_name
        }

    @classmethod
    def create_chart_data(cls, chart, data):
        x_axis = chart.meta_data["metadata"]["x_axis"]
        y_axis = chart.meta_data["metadata"]["y_axis"]

        color_palette = ColorPalette()
        border_colors, background_colors  = color_palette.get_colors(len(data[x_axis]))
        return {
            "type": "pie",
            "data": {
                "labels": data[x_axis],
                "datasets": [{
                    "data": data[y_axis],
                    "borderWidth": 1,
                    "borderColor": border_colors,
                    "backgroundColor": background_colors,
                }]
            },
            "options": {
                "maintainAspectRatio": False,
            }
        }
