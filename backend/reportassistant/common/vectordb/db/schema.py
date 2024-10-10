import logging

from pymilvus import FieldSchema, DataType, CollectionSchema


from common.vectordb.db.client import get_client
from common.vectordb.embeddings import BgeM3EmbeddingsModel

logger = logging.getLogger(__name__)

def create_collection(collection_name: str):
    """
    Create schema for the data
    Args:
        collection_name: The name of the collection.

    Returns:

    """
    fields = [
        FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, auto_id=True, max_length=100),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=10_000),
        FieldSchema(name="sparse_vector", dtype=DataType.SPARSE_FLOAT_VECTOR),
        FieldSchema(name="dense_vector", dtype=DataType.FLOAT_VECTOR, dim=BgeM3EmbeddingsModel.get_dense_dim()),
        FieldSchema(name="database_name", dtype=DataType.VARCHAR, max_length=2048),
        FieldSchema(name="schema_name", dtype=DataType.VARCHAR, max_length=2048),
        FieldSchema(name="table_name", dtype=DataType.VARCHAR, max_length=2048),
    ]

    with get_client() as client:
        try:
            # Create the collection schema
            schema = CollectionSchema(fields, description="Table use cases")

            # Create the collection using the client
            client.create_collection(collection_name, schema=schema)

            client.add_index(field_name="sparse_vector", metric_type="IP", index_type="SPARSE_INVERTED_INDEX")
            client.add_index(field_name="dense_vector",  metric_type="IP", index_type="FLAT")

            # Load the collection into memory
            client.load_collection(collection_name)

        except Exception as e:
            logger.error(f"Error during create {collection_name} collection: {str(e)}")
            raise e