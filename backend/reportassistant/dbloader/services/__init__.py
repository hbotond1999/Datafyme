import dataclasses

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
        self.create_realiation_graph()


    def vector_loader(self):
        tables_schemas = self.extractor.get_tables_schemas()
        try:
            VectorLoader(tables_schemas, self.datasource).load()
        except Exception as e:
            return str(e)

    def create_realiation_graph(self):

        database_relations = self.extractor.get_relations()

        defined_relations = [dataclasses.asdict(t) for t in database_relations]

        table_previews = self.extractor.get_table_previews()
        found_relations = RelationFinder(table_previews).find_relation()
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

            return

        except:
            return "Graph creation failed"
        finally:
            neo4j_instance.close()