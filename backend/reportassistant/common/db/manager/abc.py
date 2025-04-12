import abc
from typing import List, Literal, Any, Dict
from db_configurator.models import DatabaseSource
from common.db.manager.types import TableSchema


class DatabaseManagerAbc(metaclass=abc.ABCMeta):

    def __init__(self, db_source: DatabaseSource):
        self.db_source = db_source

    @abc.abstractmethod
    def get_table_names_with_schema(self) -> List[str]:
        pass

    @abc.abstractmethod
    def get_table_schema(self, table_name: str) -> TableSchema:
        pass

    @abc.abstractmethod
    def get_tables_schemas(self) -> List[TableSchema]:
        pass

    @abc.abstractmethod
    def get_relations(self):
        pass

    @abc.abstractmethod
    def get_table_previews(self):
        pass

    @abc.abstractmethod
    def execute_sql(self, sql: str, response_format: Literal["dict", "list", "series", "split", "tight", "index"] = 'list', row_num: int = None):
        pass

    @abc.abstractmethod
    def check_connection(self) -> bool:
        pass

    @abc.abstractmethod
    def get_table_ddl(self, table_name: str) -> str:
        pass

    @abc.abstractmethod
    def create_schema(self, schema_name: str):
        pass

    @abc.abstractmethod
    def check_schema_exists(self, schema_name: str) -> bool:
        pass

    @abc.abstractmethod
    def drop_schema(self, schema_name: str):
        pass