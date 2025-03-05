import logging
from typing import List

from attr import dataclass
from pymilvus import FieldSchema, DataType, CollectionSchema, MilvusClient, Collection

from common.vectordb.embeddings import BgeM3EmbeddingsModel

logger = logging.getLogger("reportassistant.default")

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
        FieldSchema(name="database_id", dtype=DataType.INT64),
    ]
    schema = CollectionSchema(fields, "")
    col_name = collection_name

    col = Collection(col_name, schema)

    sparse_index = {"index_type": "SPARSE_INVERTED_INDEX", "metric_type": "IP"}
    col.create_index("sparse_vector", sparse_index)
    dense_index = {"index_type": "FLAT", "metric_type": "IP"}
    col.create_index("dense_vector", dense_index)
    col.load()


@dataclass
class TableDocument:
    text: str
    database_name: str
    database_id: int
    schema_name: str
    table_name: str
    distance: float = None

def convert_to_milvus_data(table_docs: List[TableDocument]):
    texts = []
    database_names = []
    schema_names = []
    table_names = []
    database_ids = []
    for table_doc in table_docs:
        texts.append(table_doc.text)
        database_names.append(table_doc.database_name)
        schema_names.append(table_doc.schema_name)
        table_names.append(table_doc.table_name)
        database_ids.append(table_doc.database_id)

    result = BgeM3EmbeddingsModel.create_sparse_dense_vectors(texts)
    return [
        texts,
        result.sparse_vectors,
        result.dense_vectors,
        database_names,
        schema_names,
        table_names,
        database_ids
    ]

