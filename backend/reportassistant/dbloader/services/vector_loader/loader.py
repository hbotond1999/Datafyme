from typing import List

from langchain.chains.base import Chain

from common.vectordb.db import create_collection, COLLECTION_NAME
from common.vectordb.db.schema import TableDocument
from common.vectordb.db.utils import insert_docs_to_collection, delete_docs_from_collection
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
        """
        Loads table documentations data into vector database.
        Args:
            None

        Returns:
            None
        """
        data = []
        table_docs = self.create_docs()
        for table_doc in table_docs:
            data.append(TableDocument(
                text=table_doc.table_description,
                table_name=table_doc.table_name,
                database_name= table_doc.database_name,
                schema_name=table_doc.schema_name)
            )

            for question in table_doc.common_queries:
                data.append(TableDocument(
                    text=question,
                    table_name=table_doc.table_name,
                    database_name= table_doc.database_name,
                    schema_name=table_doc.schema_name)
                )
            for use_case in table_doc.use_cases:
                data.append(TableDocument(
                    text=use_case,
                    table_name=table_doc.table_name,
                    database_name=table_doc.database_name,
                    schema_name=table_doc.schema_name)
                )
        delete_docs_from_collection(collection_name=COLLECTION_NAME, column_name="database_name", value=self.db_name)
        insert_docs_to_collection(data, COLLECTION_NAME)