import asyncio
import json
from datetime import datetime
import logging

from common.db.manager.database_manager import DatabaseManager
from common.graph_db.graph_db import Neo4JInstance
from common.vectordb.db.utils import hybrid_search
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.agents import sql_agent, refine_user_question_agent
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.reranker import grade_ddls

from reporter_agent.reporter.subgraph.sql_statement_creator.ai.state import GraphState


logger = logging.getLogger('reportassistant.custom')


def hybrid_search_node(state: GraphState):
    """
    Args:
        state (GraphState):

    Returns:
        dict: A dictionary containing the matching_tables
    """
    collection_name = "TablesDocs"
    similar_docs = hybrid_search(state["message"], collection_name, database_id=state["database_source"].id, limit=15)
    tables = []
    seen = set()
    for table_doc in similar_docs:
        key = (table_doc.schema_name, table_doc.table_name)
        if key not in seen:
            seen.add(key)
            tables.append({'schema': table_doc.schema_name, 'table_name': table_doc.table_name})
    return {"matching_tables": tables}


def get_ddls(state: GraphState):
    """
    Args:
        state (GraphState):

    Returns:
        dict: A dictionary containing the matching_tables
    """
    extractor = DatabaseManager(state["database_source"])
    tables_schemas = extractor.get_tables_schemas()
    matching_tables = [f'{temp["schema"]}.{temp["table_name"]}' for temp in state["matching_tables"]]
    json_data = [table.to_dict() for table in tables_schemas if f'{table.schema}.{table.name}' in matching_tables]
    return {"matching_table_ddls": json_data}


def reranker(state: GraphState):
    filtered_ddls = asyncio.run(grade_ddls(state))
    return {"filtered_table_ddls": filtered_ddls}


def refine_user_question(state: GraphState):
    refine_recursive_limit = state["refine_recursive_limit"] - 1
    logger.info(f"Actual REFINE RECURSIVE LIMIT value: {refine_recursive_limit}")

    if refine_recursive_limit >= 0:
        result = refine_user_question_agent().invoke({'message': state["message"]})
        return {"message": result.message, "refine_recursive_limit": refine_recursive_limit}
    else:
        logger.error(f"Refine user message recursive limit exceeded")
        raise SystemExit("Refine user message recursive limit exceeded")


def relation_graph(state: GraphState):
    filtered_tables = [(table["schema"], table["name"]) for table in state['filtered_table_ddls']]
    neo4j_instance = Neo4JInstance()

    tables_all = []
    seen = set()
    for schema_name, table_name in filtered_tables:
        key = (schema_name, table_name)
        if key not in seen:
            seen.add(key)
            tables_all.append({"schema": schema_name, "table_name": table_name})
        for neighbour in neo4j_instance.find_table_neighbours(state["database_source"].id, schema_name, table_name):
            key2 = (neighbour['neighbour_schema'], neighbour['neighbour_table_name'])
            if key2 not in seen:
                tables_all.append({"schema": neighbour['neighbour_schema'],
                                   "table_name": neighbour['neighbour_table_name']})

    neo4j_instance.close()
    return {"tables_all": tables_all}


def get_final_ddls(state: GraphState):
    extractor = DatabaseManager(state["database_source"])
    tables_schemas = extractor.get_tables_schemas()
    matching_tables = [f'{temp["schema"]}.{temp["table_name"]}' for temp in state["tables_all"]]
    json_data = [table.to_dict() for table in tables_schemas if f'{table.schema}.{table.name}' in matching_tables]
    return {"table_final_ddls": json_data}


def create_query(state: GraphState):
    """
    Args:
        state (GraphState): A dictionary-like object containing the current state of the graph
                            that includes 'table_final_ddls', 'database_source' and 'message'.

    Returns:
        dict: A dictionary containing the 'result_query' derived from the result of invoking
              the sql agent.
    """
    result = sql_agent().invoke({'ddls': json.dumps(state["table_final_ddls"]),
                                 'message': state["message"],
                                 'database': state["database_source"].type,
                                 'systemtime': datetime.now().isoformat()})
    return {"sql_query": result.sql_query, "query_description": result.query_description,
            "table_final_ddls": state["table_final_ddls"]}
