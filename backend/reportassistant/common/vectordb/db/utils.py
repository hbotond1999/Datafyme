import logging
from typing import List

from pymilvus import Collection, AnnSearchRequest, RRFRanker

from common.vectordb.db import COLLECTION_NAME
from common.vectordb.db.schema import TableDocument, convert_to_milvus_data
from common.vectordb.embeddings import BgeM3EmbeddingsModel

logger = logging.getLogger(__name__)

def insert_docs_to_collection(table_docs: List[TableDocument], collection_name: str = COLLECTION_NAME):
    try:
        Collection(collection_name).insert(convert_to_milvus_data(table_docs))
    except Exception as e:
        logger.error(f"Error during insertion of docs to {collection_name}")
        raise e


def hybrid_search(query: str, collection_name: str, limit: int = 50):
    """
    Hybrid search for documents. Semantic and keyword search is combined
    Args:
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
    sparse_req = AnnSearchRequest(query_embeddings["sparse"],"sparse_vector", sparse_search_params, limit=limit)
    dense_search_params = {"metric_type": "IP"}
    dense_req = AnnSearchRequest(query_embeddings["dense"], "dense_vector", dense_search_params, limit=limit)

    res = col.hybrid_search([sparse_req, dense_req], rerank=RRFRanker(),
                            limit=limit, output_fields=['text', "source", "title"])
    result = []
    for hit in res:
        result.append(
            TableDocument(
                table_name=hit.fields["table_name"],
                database_name=hit.fields["database_name"],
                schema_name=hit.fields["schema_name"],
                text=hit.fields["text"],
                distance=hit.distance,
            )
        )
    return sorted(result, key=lambda item: item.distance, reverse=False)