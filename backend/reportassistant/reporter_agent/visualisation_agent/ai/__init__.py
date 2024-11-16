from enum import Enum
from typing import Dict, List, Union, Any

from pydantic import BaseModel

from reporter_agent.visualisation_agent.chart import ChartTypes


class RepType(Enum):
    CHART= 'CHART'
    TABLE='TABLE'
    TEXT = 'TEXT'


class FinalData(BaseModel):
    type: RepType
    chart_type: ChartTypes | None
    data: str | Dict[str, List[Any]] | Dict[str, Dict[str, Union[str, List[Any]]]]
