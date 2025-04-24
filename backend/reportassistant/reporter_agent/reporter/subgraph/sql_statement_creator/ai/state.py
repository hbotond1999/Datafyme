from typing import TypedDict, Dict, List, Any

from db_configurator.models import DatabaseSource


class GraphState(TypedDict):
    """
        GraphState is a TypedDict that describes the state of a graph with various attributes.

        Attributes:
            matching_tables: A list of dicts containing matching schema, table pairs.

    """
    message: str
    database_source: DatabaseSource
    matching_tables: List[Dict[str, str]]
    matching_table_ddls: List[Dict[str, Any]]
    filtered_table_ddls: List[Dict[str, Any]]
    tables_all: List[Dict[str, str]]
    table_final_ddls: List[Dict[str, Any]]
    sql_query: str
    language: str
    query_description: str
    refine_recursive_limit: int
