import logging
from typing import List, Literal

from common.db.manager.handlers.utils.exception import ExecuteQueryError
from db_configurator.models import DatabaseSource
from common.db.manager.abc import DatabaseManagerAbc
from common.db.manager.handlers import HANDLER
from common.db.manager.types import TableSchema, Relation, TablePreview

logger = logging.getLogger("reportassistant.default")


class DatabaseManager(DatabaseManagerAbc):


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

    def get_relations(self) -> List[Relation]:
        try:
            return self.handler.get_relations()
        except Exception as e:
            logger.error(f"An error occurred while getting table relations: {e}")
            raise e

    def get_table_previews(self) -> List[TablePreview]:
        try:
            return self.handler.get_table_previews()
        except Exception as e:
            logger.error(f"An error occurred while getting table previews: {e}")
            raise e

    def execute_sql(self, sql: str, response_format: Literal["dict", "list", "series", "split", "tight", "index"] = 'list', row_num: int = None):
        try:
            return self.handler.execute_sql(sql, response_format, row_num)
        except Exception as e:
            raise ExecuteQueryError(f"Failed to execute query: {sql}", original_exception=e)

    def check_connection(self) -> bool:
        return self.handler.check_connection()

    def get_table_ddl(self, table_name: str) -> str:
        return self.handler.get_table_ddl(table_name)

    def create_schema(self, schema_name: str):
        self.handler.create_schema(schema_name)

    def check_schema_exists(self, schema_name: str) -> bool:
        return self.handler.check_schema_exists(schema_name)

    def drop_schema(self, schema_name: str):
        self.handler.drop_schema(schema_name)