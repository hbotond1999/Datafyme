import logging
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, AnyStr, Any, Literal

import pandas as pd
from numpy.f2py.auxfuncs import throw_error

from common.custom_logging import log
from common.db.manager.handlers.utils.postgres_helper import PostgresHelper
from db_configurator.models import DatabaseSource
from common.db.manager.abc import DatabaseManagerAbc
from common.db.manager.types import TableSchema, Column, Relation, TablePreview

logger = logging.getLogger(__name__)


class PostgresDatabaseManager(DatabaseManagerAbc):

    def __init__(self, db_source: DatabaseSource):
        super().__init__(db_source)
        self.db_manager = PostgresHelper(
            dbname=db_source.name,
            user=db_source.username,
            password=db_source.password,
            host=db_source.host,
            port=db_source.port
        )


    def get_table_ddl(self, table_name) -> TableSchema:
        try:
            schema, table = table_name.split('.')
            result = self.db_manager.execute_query(f"""
                WITH table_info AS (
              SELECT c.oid, c.relname, n.nspname
              FROM pg_class c
              JOIN pg_namespace n ON c.relnamespace = n.oid
              WHERE c.relname = '{table}'  
                AND n.nspname = '{schema}' 
            ),
            cols AS (
              SELECT a.attrelid,
                     string_agg(
                       '    ' || quote_ident(a.attname) || ' ' || pg_catalog.format_type(a.atttypid, a.atttypmod)
                       || CASE WHEN a.attnotnull THEN ' NOT NULL' ELSE '' END
                       || CASE WHEN a.atthasdef THEN ' DEFAULT ' || pg_get_expr(ad.adbin, ad.adrelid) ELSE '' END,
                       E',\n' ORDER BY a.attnum
                     ) AS col_defs
              FROM pg_attribute a
              LEFT JOIN pg_attrdef ad
                ON ad.adrelid = a.attrelid AND ad.adnum = a.attnum
              WHERE a.attrelid = (SELECT oid FROM table_info)
                AND a.attnum > 0
                AND NOT a.attisdropped
              GROUP BY a.attrelid
            ),
            cons AS (
              SELECT con.conrelid,
                     string_agg(
                       '    CONSTRAINT ' || quote_ident(con.conname) || ' ' || pg_get_constraintdef(con.oid),
                       E',\n' ORDER BY con.conname
                     ) AS con_defs
              FROM pg_constraint con
              WHERE con.conrelid = (SELECT oid FROM table_info)
              GROUP BY con.conrelid
            )
            SELECT 'CREATE TABLE ' || quote_ident(t.nspname) || '.' || quote_ident(t.relname) || E' (\n' ||
                   COALESCE(c.col_defs, '') ||
                   CASE WHEN con.con_defs IS NOT NULL THEN E',\n' || con.con_defs ELSE '' END ||
                   E'\n);' AS ddl
            FROM table_info t
            LEFT JOIN cols c ON t.oid = c.attrelid
            LEFT JOIN cons con ON t.oid = con.conrelid;
            """)

            if result and isinstance(result, list) and len(result) > 0:
                print(result)
                return TableSchema(name=table_name, schema=schema, columns=[], ddl=result[0]["ddl"])
            else:
                raise Exception("Table not exists: " + table_name)
        except Exception as e:
            logger.error(f"An error occurred while fetching DDL for table {table_name}: {e}")
            raise e

    @log()
    def get_tables_ddls(self) -> List[TableSchema]:
        table_names = self.get_table_names_with_schema()
        table_list = []

        for table_name in table_names:
            table = self.get_table_ddl(table_name)
            table_list.append(table)

        return table_list

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

    def get_relations(self) -> List[Relation]:
        try:
            result = self.db_manager.execute_query("""
            select distinct 
                tc.constraint_name, 
                tc.table_name, 
                tc.table_schema,
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                ccu.table_schema as foreign_table_schema
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type in ('FOREIGN KEY');
            """)

            if result and isinstance(result, list):
                relations = [
                    Relation(
                        constraint_name=row['constraint_name'],
                        table_schema=row['table_schema'],
                        table_name=row['table_name'],
                        column_name=row['column_name'],
                        foreign_table_schema=row['foreign_table_schema'],
                        foreign_table_name=row['foreign_table_name'],
                        foreign_column_name=row['foreign_column_name']
                    ) for row in result
                ]

                return relations
            else:
                logger.warning("No relations found in the database.")
                return []
        except Exception as e:
            logger.error(f"An error occurred while fetching table names: {e}")
            raise e

    def get_table_previews(self):
        try:
            # Fetch all table names with schema
            table_names = self.get_table_names_with_schema()
            table_list = []

            for table_name in table_names:
                table = self.preview(table_name)
                table_list.append(table)

            return table_list

        except Exception as e:
            logger.error(f"An error occurred while fetching preview for all tables: {e}")
            raise e

    def preview(self, table_name: str):
        try:
            schema, table = table_name.split('.')

            # Query to get column definitions for the specified table
            query = f"""
            SELECT 
                *
            FROM {schema}.{table}
            LIMIT 10;
            """

            # Execute the query
            result = self.db_manager.execute_query(query)

            if result and isinstance(result, list):
                result_df = pd.DataFrame(result)
                markdown_table = result_df.to_markdown(index=False)
                return TablePreview(schema=schema, table_name=table, markdown_preview=markdown_table)
            else:
                logger.warning(f"No columns found for table {table_name}")
                raise Exception(f"No columns found for table {table_name}")

        except Exception as e:
            logger.error(f"An error occurred while fetching preview for table {table_name}: {e}")
            raise e


    def execute_sql(self, sql: str, response_format: Literal["dict", "list", "series", "split", "tight", "index"] = 'list'):
        try:
            result = self.db_manager.execute_query(sql)
            if result and isinstance(result, list):
                result_df = pd.DataFrame(result)
                if response_format == "list":
                    return self._convert_to_serializable_dict(result_df.to_dict(orient=response_format))
                return result_df.to_dict(orient=response_format)
        except Exception as e:
            logger.error(f"An error occurred while execute query: {e}")
            raise e

    def check_connection(self) -> bool:
        return self.db_manager.check_connection()


    def _convert_to_serializable(self, record: Any) -> Any:
        if isinstance(record, (pd.Timestamp, datetime)):
            return record.isoformat()
        elif isinstance(record, date):
            return record.isoformat()
        elif isinstance(record, Decimal):
            return float(record)
        return record

    def _convert_to_serializable_dict(self, data: Dict[str, List[Any]]):
        return {
            key: [self._convert_to_serializable(record) for record in values]
            for key, values in data.items()
        }