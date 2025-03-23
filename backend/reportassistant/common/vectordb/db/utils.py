import logging
from typing import List, Union

from pymilvus import Collection, AnnSearchRequest, RRFRanker

from common.vectordb.db import COLLECTION_NAME
from common.vectordb.db.schema import TableDocument, convert_to_milvus_data
from common.vectordb.embeddings import BgeM3EmbeddingsModel

logger = logging.getLogger("reportassistant.default")

def insert_docs_to_collection(table_docs: List[TableDocument], collection_name: str = COLLECTION_NAME):
    """
    Insert table use cases to vector database
    Args:
        table_docs (List[TableDocument]): A list of table use cases to be inserted.
        collection_name (str, optional): The name of the collection into which the documents

    Raises:
        Exception: Re-raises any exception encountered during the insertion process.
    """
    try:
        Collection(collection_name).insert(convert_to_milvus_data(table_docs))
    except Exception as e:
        logger.error(f"Error during insertion of docs to {collection_name} " + str(e))
        raise e


def hybrid_search(query: str, collection_name: str, database_id: int, limit: int = 50):
    """
    Hybrid search for documents. Semantic and keyword search is combined
    Args:
        database_id: database id
        query: User query. Search text.
        limit: If the reranker is enabled, we retrieve this many documents from the vector database, and the reranker
        narrows it down to the top_k number of items.
        collection_name:  The name of the collection.
    Returns:
        Similar documents
    """

    col = Collection(collection_name)

    query_embeddings = BgeM3EmbeddingsModel.get_model()([query])

    sparse_search_params = {"metric_type": "IP"}
    sparse_req = AnnSearchRequest(query_embeddings["sparse"],"sparse_vector", sparse_search_params, limit=limit, expr=f"database_id=={database_id}")
    dense_search_params = {"metric_type": "IP"}
    dense_req = AnnSearchRequest(query_embeddings["dense"], "dense_vector", dense_search_params, limit=limit, expr=f"database_id=={database_id}")

    res = col.hybrid_search([sparse_req, dense_req], rerank=RRFRanker(),
                            limit=limit, output_fields=['table_name', "database_name", "schema_name", "text", "database_id"])
    res = res[0]
    result = []
    for hit in res:
        result.append(
            TableDocument(
                table_name=hit.fields["table_name"],
                database_name=hit.fields["database_name"],
                schema_name=hit.fields["schema_name"],
                text=hit.fields["text"],
                distance=hit.distance,
                database_id=hit.fields["database_id"]
            )
        )
    return sorted(result, key=lambda item: item.distance, reverse=False)


def delete_docs_from_collection(column_name: str, value: Union[str, int], collection_name: str):
    """
    Args:
        column_name: The name of the column to filter the documents by.
        value: The value to match in the specified column which determines the documents to delete. Can be a string or an integer.
        collection_name: The name of the collection from which documents will be deleted.

    """
    col = Collection(collection_name)
    if isinstance(value,str):
        col.delete(f"""{column_name} in ["{value}"]""")
    elif isinstance(value, int):
        col.delete(f"""{column_name} in [{value}]""")
