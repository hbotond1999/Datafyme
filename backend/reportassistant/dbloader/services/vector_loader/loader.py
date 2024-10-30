from typing import List

from langchain.chains.base import Chain

from dbloader.services.utils.db_schema.types import TableSchema
from dbloader.services.vector_loader.ai.doc_agent import create_doc_agent
from dbloader.services.vector_loader.ai.response import TableDocumentation


class VectorLoader:
    table_schemas: List[TableSchema]
    documentation_agent: Chain
    db_name: str

    def __init__(self, table_schemas: List[TableSchema], db_name: str):
        """
        :param table_schemas: List of TableSchema objects defining the schema for each table.
        """
        self.table_schemas = table_schemas
        self.documentation_agent = create_doc_agent()
        self.db_name = db_name

    def create_docs(self) -> List[TableDocumentation]:
        """
        Creates and returns documentation for each table schema in the list of table schemas.

        :return: List of generated documentation for each table schema.
        """
        table_docs = []
        for table_schema in self.table_schemas:
            table_doc: TableDocumentation = self.documentation_agent.invoke({"table_schema": table_schema.to_dict()})
            table_doc.table_name = table_schema.name
            table_doc.schema_name = table_schema.schema
            table_doc.database_name = self.db_name
            table_docs.append(table_doc)
        return table_docs

    def load(self) -> None:
        table_docs = self.create_docs()
        print(table_docs)