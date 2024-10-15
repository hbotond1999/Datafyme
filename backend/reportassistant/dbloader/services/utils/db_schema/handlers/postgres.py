import logging
from typing import List

from common.db.postgres import PostgresDatabaseManager
from db_configurator.models import DatabaseSource
from dbloader.services.utils.db_schema.abc import SchemaExtractor
from dbloader.services.utils.db_schema.types import TableSchema, Column

logger = logging.getLogger(__name__)


class PostgresSchemaExtractor(SchemaExtractor):

    def __init__(self, db_source: DatabaseSource):
        super().__init__(db_source)
        self.db_manager = PostgresDatabaseManager(
            dbname=db_source.name,
            user=db_source.username,
            password=db_source.password,
            host=db_source.host,
            port=db_source.port
        )

    def get_table_schema(self, table_name: str) -> TableSchema:
        try:
            schema, table = table_name.split('.')

            # Query to get column definitions for the specified table
            query = f"""
            SELECT 
                c.column_name,
                c.data_type,
                c.is_nullable
            FROM information_schema.columns AS c
            WHERE c.table_name = '{table}' 
            AND c.table_schema = '{schema}';
            """

            # Execute the query
            result = self.db_manager.execute_query(query)

            if result and isinstance(result, list):
                # Construct the column definitions
                columns = [
                    Column(
                        name=row['column_name'],
                        data_type=row['data_type'],
                        nullable=row['is_nullable'] == 'YES'
                    ) for row in result
                ]

                return TableSchema(name=table, schema=schema, columns=columns)
            else:
                logger.warning(f"No columns found for table {table_name}")
                raise Exception(f"No columns found for table {table_name}")

        except Exception as e:
            logger.error(f"An error occurred while fetching DDL for table {table_name}: {e}")
            raise e

    def get_table_names_with_schema(self) -> List[str]:
        try:
            # Execute the query to get table names with schema
            result = self.db_manager.execute_query("""
            SELECT schemaname || '.' || tablename as full_table_name
            FROM pg_catalog.pg_tables
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog');
            """)

            if result and isinstance(result, list):
                return [row["full_table_name"] for row in result]
            else:
                logger.warning("No tables found in the database.")
                return []

        except Exception as e:
            logger.error(f"An error occurred while fetching table names: {e}")
            raise e

    def get_tables_schemas(self) -> List[TableSchema]:
        try:
            # Fetch all table names with schema
            table_names = self.get_table_names_with_schema()
            table_list = []

            for table_name in table_names:
                table = self.get_table_schema(table_name)
                table_list.append(table)

            return table_list

        except Exception as e:
            logger.error(f"An error occurred while fetching DDL for all tables: {e}")
            raise e
