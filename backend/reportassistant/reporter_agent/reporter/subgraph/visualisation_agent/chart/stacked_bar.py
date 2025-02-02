from collections import defaultdict
from typing import Optional

from pydantic import BaseModel, Field

from reporter_agent.reporter.subgraph.visualisation_agent.chart.abc import Chart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.color import ColorPalette
from reporter_agent.reporter.subgraph.visualisation_agent.chart.utils import axis_date_str_converter


class StackedBarChart(BaseModel, Chart):
    x_axis_column_name: str = Field( description="This x axis displays the categories or groups being compared. Each bar corresponds to one category, such as different products, countries.")
    y_value_column_name: str = Field(description="This represents the values that are being measured and visualized on the y-axis.")
    category_column_name: str = Field( description="This column defines the categories that break down the bars into segments, representing different parts of each total value.")
    date_format: Optional[str] = Field( description='The date format to use, to show values of the x_axis_column in the chart. It should be Python strftime method compatible.', default=None)
    def create_meta_data(self):
        return {
            "x_axis": self.x_axis_column_name,
            "y_axis": self.y_value_column_name,
            "category_column_name": self.category_column_name,
            "date_format": self.date_format
        }

    @classmethod
    def create_chart_data(cls, chart, data):
        date_format = chart.meta_data["metadata"].get("date_format", None)
        raw_labels = data[chart.meta_data["metadata"]["x_axis"]]
        if not date_format:
            labels =  list(set(data[chart.meta_data["metadata"]["x_axis"]]))
        else:
            labels = axis_date_str_converter(dates=list(set(data[chart.meta_data["metadata"]["x_axis"]])), date_format=date_format)

        y_axis = chart.meta_data["metadata"]["y_axis"]
        category = chart.meta_data["metadata"]["category_column_name"]

        uniques_categories = list(set(data[category]))
        color_palette = ColorPalette()
        colors_without_opacity, colors_with_opacity = color_palette.get_colors( len(uniques_categories))
        category_color_map = {item: {"backgroundColor": colors_with_opacity[i], "borderColor": colors_without_opacity[i]}  for i, item in enumerate(uniques_categories)}

        stack_data = {}
        for category_value, y_value in zip(data[category], data[y_axis]):
            if stack_data.get(category_value) is None:
                stack_data[category_value] = [y_value]
            else:
                stack_data[category_value].append(y_value)

        datasets = []
        for category_value in stack_data:
            datasets.append({
                "label": category_value,
                "data": stack_data[category_value],
                "backgroundColor": category_color_map[category_value]["backgroundColor"],
                "borderColor": category_color_map[category_value]["borderColor"],
                "borderWidth": 1,
                "stack": category_value
            })
        return {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": datasets
            },
            "options": {
                "maintainAspectRatio": False,
                "scales": {
                    "x": {
                        "stacked": True
                    },
                    "y": {
                        "stacked": True,
                        "beginAtZero": True
                    }
                }
            }
        }
