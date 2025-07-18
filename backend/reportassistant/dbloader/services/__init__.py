import dataclasses

from ir_datasets.datasets.touche_image import dataset

from common.db.manager.database_manager import DatabaseManager
from common.graph_db.graph_db import Neo4JInstance
from db_configurator.models import DatabaseSource
from dbloader.services.graph_loader.relation_finder import RelationFinder
from dbloader.services.vector_loader.loader import VectorLoader


class DBLoader:
    def __init__(self, datasource: DatabaseSource):
        self.datasource = datasource
        self.extractor = DatabaseManager(datasource)

    def load(self):
        self.vector_loader()
        self.create_relation_graph()

    def vector_loader(self):
        tables_schemas = self.extractor.get_tables_schemas()
        tables_schemas = self.filter_schemas(tables_schemas)
        VectorLoader(tables_schemas, self.datasource).load()

    def create_relation_graph(self):

        database_relations = self.extractor.get_relations()
        defined_relations = []
        for dr in database_relations:
            if dr.table_schema == self.datasource.schema_name:
                defined_relations.append(dr)

        tables_schemas = self.extractor.get_tables_schemas()
        tables_schemas = self.filter_schemas(tables_schemas)
        table_ddls = [table.to_dict() for table in tables_schemas]
        found_relations = RelationFinder(table_ddls).find_relation()
        found_relations = [rel.model_dump() for rel in found_relations.relations]

        relations = defined_relations + found_relations
        if relations:
            table_foreign_pairs = []
            for relation in relations:
                if relation is not None:
                    table_schema = relation.get("table_schema")
                    table_name = relation.get("table_name")
                    column_name = relation.get("column_name")
                    foreign_table_schema = relation.get("foreign_table_schema")
                    foreign_table_name = relation.get("foreign_table_name")
                    foreign_column_name = relation.get("foreign_column_name")

                    if table_name and foreign_table_name:
                        edge = {
                            "database_id": self.datasource.id,
                            "table_schema": table_schema,
                            "table_name": table_name,
                            "column_name": column_name,
                            "foreign_table_schema": foreign_table_schema,
                            "foreign_table_name": foreign_table_name,
                            "foreign_column_name": foreign_column_name
                        }

                        if edge not in table_foreign_pairs:
                            table_foreign_pairs.append(edge)
        else:
            return

        neo4j_instance = Neo4JInstance()

        try:
            for table_pair in table_foreign_pairs:
                neo4j_instance.create_relation(table_pair["database_id"],
                                               table_pair["table_schema"],
                                               table_pair["table_name"],
                                               table_pair["column_name"],
                                               table_pair["foreign_table_schema"],
                                               table_pair["foreign_table_name"],
                                               table_pair["foreign_column_name"])
        finally:
            neo4j_instance.close()

    def filter_schemas(self, tables_schemas):
        if not self.datasource.schema_name:
            return tables_schemas

        filtered_schemas = []
        for table_schema in tables_schemas:
            if table_schema.schema == self.datasource.schema_name:
                filtered_schemas.append(table_schema)
        return filtered_schemas