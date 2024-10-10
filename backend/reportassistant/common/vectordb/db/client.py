import logging
import os
from contextlib import contextmanager

from pymilvus import MilvusClient

logger = logging.getLogger(__name__)

@contextmanager
def get_client() -> MilvusClient:
    """Context manager to ensure safe creation and closing of the client connection."""
    client = MilvusClient(uri=os.getenv('VECTORDB_URI'), token=os.getenv('VECTORDB_AUTH'))
    try:
        yield client
    except Exception as e:
        logger.error(f"Error during Milvus client operation: {str(e)}")
        raise e
    finally:
        client.close()