import abc
from typing import Dict


class Chart(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def create_meta_data(self) -> Dict[str, str]:
        pass