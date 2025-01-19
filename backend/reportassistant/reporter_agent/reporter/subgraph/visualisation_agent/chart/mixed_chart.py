from typing import Dict, List, Optional, Literal

from pydantic import BaseModel, Field

from reporter_agent.reporter.subgraph.visualisation_agent.chart.abc import Chart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.utils import axis_date_str_converter


class Dataset(BaseModel):
    type: Literal["bar", "line", "scatter"] = Field(description='The chart type')
    data_column_name: str  = Field(description='The chart data to show')


class MixedChart(BaseModel, Chart):
    datasets: List[Dataset] = Field(description="The list of datasets, that show on chart")
    labels_column_name: str = Field(description='The column name to show in the chart.')
    date_format: Optional[str] = Field(description='The date format to use, to show values of the x_axis_column in the chart. It should be Python strftime method compatible.', default=None)

    def create_meta_data(self) -> Dict[str, str]:
        return self.model_dump()


    @classmethod
    def create_chart_data(cls, chart, data):
        datasets = [{"type": dataset["type"], "data": data[dataset["data_column_name"]], "label": dataset["data_column_name"]} for dataset in chart.meta_data["metadata"]["datasets"]]
        labels_raw = data[chart.meta_data["metadata"]["labels_column_name"]]
        date_format = chart.meta_data["metadata"]["date_format"]
        if date_format:
            labels = axis_date_str_converter(labels_raw, date_format)
        else:
            labels = labels_raw

        return {

            "data": {
                "datasets": datasets,
                "labels": labels
            },
            "options": {
                "maintainAspectRatio": False,
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }