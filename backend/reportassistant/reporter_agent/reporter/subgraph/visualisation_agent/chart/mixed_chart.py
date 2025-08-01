from typing import Dict, List, Optional, Literal

import pandas as pd
from pydantic import BaseModel, Field

from reporter_agent.reporter.subgraph.visualisation_agent.chart.abc import Chart
from reporter_agent.reporter.subgraph.visualisation_agent.chart.utils import axis_date_str_converter


class Dataset(BaseModel):
    type: Literal["bar", "line", "scatter"] = Field(description='The chart type')
    data_column_name: str  = Field(description='The chart data to show')


class MixedChart(BaseModel, Chart):
    datasets: List[Dataset] = Field(description="The list of datasets, that show on chart")
    labels_column_name: str = Field(description='The column name to show in the chart.')
    date_or_date_time_format: Optional[str] = Field(description='The date or date time format to use, to show values of the x_axis_column in the chart. It should be Python strftime method compatible.', default=None)

    def create_meta_data(self) -> Dict[str, str]:
        return self.model_dump()


    @classmethod
    def create_chart_data(cls, chart, data):
        datasets = [{"type": dataset["type"], "data": data[dataset["data_column_name"]], "label": dataset["data_column_name"]} for dataset in chart.meta_data["metadata"]["datasets"]]
        labels_raw = data[chart.meta_data["metadata"]["labels_column_name"]]
        date_format = chart.meta_data["metadata"]["date_or_date_time_format"]
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

    @classmethod
    def create_pptx_chart(cls, chart_metadata, data: pd.DataFrame, slide, x, y, cx, cy):
        return None

    def validate_chart_data(self, column_names: List[str]) -> List[str]:
        error_messages = []

        if self.labels_column_name not in column_names:
            error_messages.append(f"The {self.labels_column_name} column is not in the dataset.")

        for i, dataset in enumerate(self.datasets):
            if dataset.data_column_name not in column_names:
                error_messages.append(f"The {dataset.data_column_name} column is not in the dataset.")
        return error_messages
