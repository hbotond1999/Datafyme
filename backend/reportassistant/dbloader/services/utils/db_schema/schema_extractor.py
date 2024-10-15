import logging
from typing import List

from db_configurator.models import DatabaseSource, DBType
from dbloader.services.utils.db_schema.abc import SchemaExtractor
from dbloader.services.utils.db_schema.handlers import HANDLER
from dbloader.services.utils.db_schema.types import TableSchema

logger = logging.getLogger(__name__)

class DatabaseSchemaExtractor(SchemaExtractor):

    def __init__(self, db_source: DatabaseSource):
        super().__init__(db_source)
        self.db_source = db_source
        # Initialize the handler class once
        self.handler = HANDLER[self.db_source.type](self.db_source)

    def get_table_names_with_schema(self) -> List[str]:
        try:
            return self.handler.get_table_names_with_schema()
        except Exception as e:
            logger.error(f"An error occurred while getting table names: {e}")
            raise e

    def get_table_schema(self, table_name: str) -> TableSchema:
        try:
            return self.handler.get_table_schema(table_name)
        except Exception as e:
            logger.error(f"An error occurred while getting DDL for table {table_name}: {e}")
            raise e


    def get_tables_schemas(self) -> List[TableSchema]:
        try:
            return self.handler.get_tables_schemas()
        except Exception as e:
            logger.error(f"An error occurred while getting tables DDL: {e}")
            raise e