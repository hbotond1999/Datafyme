import logging
import os

from dotenv import load_dotenv
from pymilvus import connections, utility

from common.vectordb.db.schema import create_collection

logger = logging.getLogger("reportassistant.default")

load_dotenv()

connections.connect("default", uri=os.getenv("VECTORDB_URI"), token=os.getenv("VECTORDB_AUTH"))

COLLECTION_NAME = "TablesDocs"


if not utility.has_collection(COLLECTION_NAME):
    logger.info(f"{COLLECTION_NAME} collection not exists. Creating...")
    create_collection(COLLECTION_NAME)
    logger.info(f"{COLLECTION_NAME} collection created.")