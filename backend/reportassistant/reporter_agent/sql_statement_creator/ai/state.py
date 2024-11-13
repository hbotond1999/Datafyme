from typing import TypedDict, Dict, List


class GraphState(TypedDict):
    """
        GraphState is a TypedDict that describes the state of a graph with various attributes.

        Attributes:
            matching_tables: A list of dicts containing matching schema, table pairs.

    """
    matching_tables: List[Dict[str, str]]
    message: str
