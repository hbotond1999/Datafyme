from common.vectordb.db.utils import hybrid_search

from reporter_agent.sql_statement_creator.ai.state import GraphState


def hybrid_search_node(state: GraphState):
    """
    Args:
        state (GraphState):

    Returns:
        dict: A dictionary containing the matching_tables
    """
    collection_name = "TablesDocs"
    print(state["message"])
    similar_docs = hybrid_search(state["message"], collection_name, limit=10)
    tables = []
    seen = set()
    for table_doc in similar_docs:
        key = (table_doc.schema_name, table_doc.table_name)
        if key not in seen:
            seen.add(key)
            tables.append({'schema': table_doc.schema_name, 'table_name': table_doc.table_name})

    return {"matching_tables": tables}
