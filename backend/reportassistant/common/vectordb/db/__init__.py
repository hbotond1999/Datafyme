import logging

from dotenv import load_dotenv

from common.vectordb.db.client import get_client
from common.vectordb.db.schema import create_collection

logger = logging.getLogger(__name__)

load_dotenv()

COLLECTION_NAME = "TableUseCases"

with get_client() as client:
    if not client.has_collection(COLLECTION_NAME):
        logger.info(f"{COLLECTION_NAME} collection not exists. Creating...")
        create_collection(COLLECTION_NAME)
        logger.info(f"{COLLECTION_NAME} collection created.")