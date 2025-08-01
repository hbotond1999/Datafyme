from typing import List, Dict, Any, Optional, Callable

from typing_extensions import TypedDict

from db_configurator.models import DatabaseSource
from reporter_agent.reporter.subgraph.visualisation_agent.ai import FinalData


class GraphState(TypedDict):
    chat_history: List[str]  # input
    question: str  # input
    database_source: DatabaseSource  # input
    table_final_ddls: List[Dict[str, Any]]  # input
    error_message: Optional[Dict[str, str]]  # local
    sql_query: str  # local
    sql_query_description: str  # local
    sql_query_result: Dict[str, List[Any]]  # local
    representation_data: FinalData  # output
    question_is_relevant: bool
    refine_sql_recursive_limit: int  # input
    refine_empty_result_recursive_limit: int  # input
    language: str
    is_sql_needed: bool
    new_chart_needed: bool
    q_and_a_answer: str
    node_started_callback: Optional[Callable[[str, str], None]]  # input

