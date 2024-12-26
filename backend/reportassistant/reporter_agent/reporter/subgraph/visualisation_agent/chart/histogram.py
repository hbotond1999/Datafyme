from pydantic import BaseModel, Field

from reporter_agent.reporter.subgraph.visualisation_agent.chart.abc import Chart


class HistogramChart(BaseModel, Chart):
    y_axis_column: str = Field(description="The Y-axis displays the count or frequency of values falling within each bin. The height of each bar represents the number of data points within that bin’s range.")

    def create_meta_data(self):
        return {
            "y_axis": self.y_axis_column
        }

    @classmethod
    def create_chart_data(cls, chart, data):
        y_axis = chart.meta_data["metadata"]["y_axis"]

        return {
            "type": "bar",
            "data": {
                "labels": [*range(len(data[y_axis]))],
                "datasets": [{
                    "label": y_axis,
                    "data": data[y_axis],
                    "backgroundColor": "rgba(75, 192, 192, 0.6)",
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderWidth": 1
                }]
            },
            "options": {
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }
