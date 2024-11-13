from typing import TypedDict, Any, Dict, List


class GraphState(TypedDict):
    representation_type: str
    chart_type: str
    chart_data: Any
    preview_data: List[Dict[str, Any]]