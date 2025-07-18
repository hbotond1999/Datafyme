import abc
from typing import Dict, List

import pandas as pd
from pydantic import Field


class Chart(metaclass=abc.ABCMeta):
    title: str = Field(description="Chart title")
    @abc.abstractmethod
    def create_meta_data(self) -> Dict[str, str]:
        pass

    @classmethod
    @abc.abstractmethod
    def create_chart_data(cls, chart, data):
        pass

    @classmethod
    @abc.abstractmethod
    def create_pptx_chart(cls, chart_metadata, data: pd.DataFrame, slide, x, y, cx, cy):
        pass

    def validate_chart_data(self, column_names: List[str]) -> List[str]:
        """
        Validate chart data with dataset column names.
        Args:
            column_names: Dataset column names

        Returns:
            List of error messages
        """
        pass
