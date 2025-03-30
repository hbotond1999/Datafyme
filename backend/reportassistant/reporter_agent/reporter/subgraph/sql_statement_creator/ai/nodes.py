import json
from datetime import datetime
import logging

from common.graph_db.graph_db import Neo4JInstance
from common.vectordb.db.utils import hybrid_search
from db_configurator.models import TableDocumentation
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.agents import sql_agent, refine_user_question_agent
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.reranker import grade_all_ddl

from reporter_agent.reporter.subgraph.sql_statement_creator.ai.state import GraphState
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.utils import RefineLimitExceededError

logger = logging.getLogger('reportassistant.custom')


def hybrid_search_node(state: GraphState):
    """
    Args:
        state (GraphState): A dictionary-like object containing the current state of the graph.

    Returns:
        dict: A dictionary containing the matching_tables derived from the result of the hybrid search.
    """
    logger.info("Running hybrid_search_node: selecting matching table descriptions for the user message with hybrid search.")
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
        state (GraphState): A dictionary-like object containing the current state of the graph.

    Returns:
        dict: A dictionary containing the matching_table_ddls filtered from the django database.
    """
    logger.info("Running get_ddls node: selecting matching table ddls from django database.")
    matching_tables = [(temp["schema"], temp["table_name"]) for temp in state["matching_tables"]]
    json_data = [TableDocumentation.objects.get(database_source=state["database_source"], schema_name=schema,
                                                table_name=table).to_dict()
                 for schema, table in matching_tables]
    return {"matching_table_ddls": json_data}


def reranker(state: GraphState):
    """
    Args:
        state (GraphState): A dictionary-like object containing the current state of the graph.

    Returns:
        dict: A dictionary containing the filtered_table_ddls derived from the result of the ddl grader agent.
    """
    logger.info("Running reranker node: we examine the relevance of the tables using an agent.")
    results = grade_all_ddl().invoke({'message': state["message"], 'ddls': state["matching_table_ddls"]})
    filtered_ddls = [ddl for relevance, ddl in zip(results, state["matching_table_ddls"]) if relevance]

    logger.info(f"Filtered tables: {[(ddl['schema_name'], ddl['table_name']) for ddl in filtered_ddls]}")
    return {"filtered_table_ddls": filtered_ddls}


def refine_user_question(state: GraphState):
    """
    Args:
        state (GraphState): A dictionary-like object containing the current state of the graph.

    Returns:
        dict: A dictionary containing the refined user message derived from the result of the refine user question
         agent.
    """
    logger.info("Running refine_user_question node: refining the incoming user message.")
    refine_recursive_limit = state["refine_recursive_limit"] - 1
    logger.info(f"Actual REFINE RECURSIVE LIMIT value: {refine_recursive_limit}")

    if refine_recursive_limit >= 0:
        result = refine_user_question_agent().invoke({'message': state["message"],
                                                      'systemtime': datetime.now().isoformat()})
        logger.info(f"The refined user message: {result.message}")
        return {"message": result.message, "refine_recursive_limit": refine_recursive_limit}
    else:
        logger.error(f"Refine user message recursive limit exceeded")
        raise RefineLimitExceededError("We cannot answer your question based on the selected database, "
                                       "please rephrase the question or try a different source.")


def relation_graph(state: GraphState):
    """
    Args:
        state (GraphState): A dictionary-like object containing the current state of the graph.

    Returns:
        dict: A dictionary containing all the relevant tables derived from the relations of the neo4j graph database.
    """
    logger.info("Running relation_graph node: selecting all the related tables from neo4j graph database.")
    filtered_tables = [(table["schema_name"], table["table_name"]) for table in state['filtered_table_ddls']]
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
    """
    Args:
        state (GraphState): A dictionary-like object containing the current state of the graph.

    Returns:
        dict: A dictionary containing the 'table_final_ddls' derived from the django database.
    """
    logger.info("Running get_final_ddls node: selecting table ddls from django database for the final table set.")
    matching_tables = [(temp["schema"], temp["table_name"]) for temp in state["tables_all"]]
    json_data = [TableDocumentation.objects.get(database_source=state["database_source"], schema_name=schema,
                                                table_name=table).to_dict()
                 for schema, table in matching_tables]
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
    logger.info("Running create_query node: creating sql query for the user question.")
    result = sql_agent().invoke({'ddls': json.dumps(state["table_final_ddls"]),
                                 'message': state["message"],
                                 'database': state["database_source"].type,
                                 'systemtime': datetime.now().isoformat()})
    return {"sql_query": result.sql_query, "query_description": result.query_description,
            "table_final_ddls": state["table_final_ddls"]}
