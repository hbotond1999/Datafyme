import json

from common.vectordb.db.utils import hybrid_search
from db_configurator.models import DatabaseSource
from dbloader.services.utils.db_schema.schema_extractor import DatabaseSchemaExtractor

from reporter_agent.sql_statement_creator.ai.state import GraphState


def hybrid_search_node(state: GraphState):
    """
    Args:
        state (GraphState):

    Returns:
        dict: A dictionary containing the matching_tables
    """
    collection_name = "TablesDocs"
    similar_docs = hybrid_search(state["message"], collection_name, limit=10)
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
    datasource, created = DatabaseSource.objects.get_or_create(
        name="postgres",
        defaults={
            "type": "postgresql",  # Set default values for other fields
            "username": "postgres",
            "password": "password",
            "host": "localhost",
            "port": 5432,
        }
    )
    if created:
        print(f"Created new DatabaseSource: {datasource}")
    else:
        print(f"Retrieved existing DatabaseSource: {datasource}")

    extractor = DatabaseSchemaExtractor(datasource)
    tables_schemas = extractor.get_tables_schemas()
    json_data = [table.to_dict() for table in tables_schemas]

    return {"matching_table_ddls": json_data}
