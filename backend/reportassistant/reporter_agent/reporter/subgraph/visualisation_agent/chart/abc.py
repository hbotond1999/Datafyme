import abc
from typing import Dict



class Chart(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def create_meta_data(self) -> Dict[str, str]:
        pass

    @classmethod
    @abc.abstractmethod
    def create_chart_data(cls, chart, data):
        pass