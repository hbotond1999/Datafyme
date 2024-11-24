import asyncio
from typing import List

from langchain.chains.base import Chain

from common.db.manager.types import TableSchema
from common.vectordb.db import COLLECTION_NAME
from common.vectordb.db.schema import TableDocument
from common.vectordb.db.utils import insert_docs_to_collection, delete_docs_from_collection
from db_configurator.models import DatabaseSource
from dbloader.services.vector_loader.ai.doc_agent import create_doc_agent
from dbloader.services.vector_loader.ai.response import TableDocumentation


class VectorLoader:
    table_schemas: List[TableSchema]
    documentation_agent: Chain
    data_source: DatabaseSource

    def __init__(self, table_schemas: List[TableSchema], data_source: DatabaseSource):
        """
        :param table_schemas: List of TableSchema objects defining the schema for each table.
        """
        self.table_schemas = table_schemas
        self.documentation_agent = create_doc_agent()
        self.data_source = data_source

    async def create_doc(self, table_schema):
        table_doc: TableDocumentation = await self.documentation_agent.ainvoke({"table_schema": table_schema.to_dict()})
        table_doc.table_name = table_schema.name
        table_doc.schema_name = table_schema.schema
        table_doc.database_name = self.data_source.name
        return table_doc


    async def create_docs(self) -> List[TableDocumentation]:
        """
        Creates and returns documentation for each table schema in the list of table schemas.

        :return: List of generated documentation for each table schema.
        """

        tasks = [self.create_doc(table_schema) for table_schema in self.table_schemas]
        # Run all tasks concurrently
        table_docs = await asyncio.gather(*tasks)
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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        table_docs = loop.run_until_complete(self.create_docs())
        loop.close()
        for table_doc in table_docs:
            data.append(TableDocument(
                text=table_doc.table_description,
                table_name=table_doc.table_name,
                database_name= table_doc.database_name,
                schema_name=table_doc.schema_name,
                database_id = self.data_source.id)
            )

            for question in table_doc.common_queries:
                data.append(TableDocument(
                    text=question,
                    table_name=table_doc.table_name,
                    database_name= table_doc.database_name,
                    schema_name=table_doc.schema_name,
                    database_id = self.data_source.id)
                )
            for use_case in table_doc.use_cases:
                data.append(TableDocument(
                    text=use_case,
                    table_name=table_doc.table_name,
                    database_name=table_doc.database_name,
                    schema_name=table_doc.schema_name,
                    database_id = self.data_source.id)
                )
        delete_docs_from_collection(collection_name=COLLECTION_NAME, column_name="database_name", value=self.data_source.id)
        insert_docs_to_collection(data, COLLECTION_NAME)