from enum import Enum
from typing import Dict, List, Union, Any, Optional

from pydantic import BaseModel

from reporter_agent.reporter.subgraph.visualisation_agent.chart import ChartTypes


class RepType(Enum):
    CHART= 'CHART'
    TABLE='TABLE'
    TEXT = 'TEXT'


class FinalData(BaseModel):
    type: RepType
    chart_type: ChartTypes | None
    chart_title: str | None
    data: str | Dict[str, List[Any]] | Dict[str, Dict[str, Optional[Union[str, List[Any]]]]]
