import abc
from typing import List
from db_configurator.models import DatabaseSource
from dbloader.services.utils.db_schema.types import TableSchema


class SchemaExtractor(metaclass=abc.ABCMeta):

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
