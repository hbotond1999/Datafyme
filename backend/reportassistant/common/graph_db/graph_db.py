import logging

import requests
from neo4j import GraphDatabase, RoutingControl
from neo4j.exceptions import DriverError, Neo4jError
import os

from dotenv import load_dotenv


load_dotenv()


class Neo4JInstance:

    def __init__(self):
        uri = f"{os.getenv("NEO4J_SCHEMA")}://{os.getenv("NEO4J_HOST")}:{os.getenv("NEO4J_PORT")}"
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        database = os.getenv("NEO4J_DATABASE")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def create_relation(self, database_id, table_schema, table_name, column_name, foreign_table_schema,
                        foreign_table_name, foreign_column_name):
        with self.driver.session() as session:
            result = self._create_and_return_relation(database_id, table_schema, table_name, column_name,
                                                      foreign_table_schema, foreign_table_name, foreign_column_name)
            print(f"Created relation between: {result['t1']}, {result['t2']}")

    def _create_and_return_relation(self, database_id, table_schema, table_name, column_name, foreign_table_schema,
                                    foreign_table_name, foreign_column_name):

        query = (
            "MERGE (t1:Table {name: $table_name, schema: $table_schema, database_id: $database_id}) "
            "MERGE (t2:Table {name: $foreign_table_name, schema: $foreign_table_schema, database_id: $database_id})"
            "MERGE (t1)-[r1:RELATED_TO { column_name: $column_name, foreign_column_name: $foreign_column_name }]->(t2)"
            "MERGE (t2)-[r2:RELATED_TO { column_name: $foreign_column_name, foreign_column_name: $column_name }]->(t1)"
            "RETURN t1.name, t2.name"
        )

        try:
            record = self.driver.execute_query(query,
                                               table_schema=table_schema,
                                               table_name=table_name,
                                               column_name=column_name,
                                               foreign_table_schema=foreign_table_schema,
                                               foreign_table_name=foreign_table_name,
                                               foreign_column_name=foreign_column_name,
                                               database_=self.database,
                                               database_id=database_id,
                                               result_transformer_=lambda r: r.single(strict=True))
            return {"t1": record["t1.name"], "t2": record["t2.name"]}

        except (DriverError, Neo4jError) as exception:
            logging.error("%s raised an error: \n%s", query, exception)
            raise

    def clear_graph_database(self, database_id):
        query = f"MATCH (n) WHERE n.database_id = '{database_id}' DETACH DELETE n"
        try:
            self.driver.execute_query(query, database_=self.database)
            logging.info(f"{database_id} database deleted")
        except (DriverError, Neo4jError) as exception:
            logging.error(f"Error occurred during database_id: {database_id} database delete: {exception}")
            raise

    def find_table_neighbours(self, database_id, schema_name, table_name):
        query = (
            "MATCH (t:Table)-[r:RELATED_TO]->(neighbour:Table) "
            "WHERE t.database_id = $database_id AND t.name = $table_name AND t.schema = $schema_name "
            "  AND neighbour.database_id = $database_id "
            "RETURN neighbour.name AS name, neighbour.schema AS schema"
        )

        results = self.driver.execute_query(query,
                                            database_id=str(database_id),
                                            schema_name=schema_name,
                                            table_name=table_name,
                                            database_=self.database,
                                            routing_=RoutingControl.READ)

        neighbours = [{"neighbour_table_name": record["name"],
                       "neighbour_schema": record["schema"]} for record in results.records]

        query = (
            "MATCH (t1:Table)-[r:RELATED_TO]->(t2:Table) "
            "WHERE t1.database_id = $database_id AND t2.database_id = $database_id "
            "  AND t1.name = $table_name AND t2.name = $neighbour_table_name "
            "  AND t1.schema = $schema_name AND t2.schema = $neighbour_schema "
            "RETURN r.column_name AS column_name, r.foreign_column_name AS foreign_column_name"
        )

        results = []
        for neighbour in neighbours:
            records, summary, keys = self.driver.execute_query(query,
                                                               database_id=str(database_id),
                                                               schema_name=schema_name,
                                                               table_name=table_name,
                                                               neighbour_schema=neighbour["neighbour_schema"],
                                                               neighbour_table_name=neighbour["neighbour_table_name"],
                                                               database_=self.database)
            relation = {
                'column_name': records[0]["column_name"],
                'foreign_column_name': records[0]["foreign_column_name"]
            }
            results.append({"neighbour_schema": neighbour["neighbour_schema"],
                            "neighbour_table_name": neighbour["neighbour_table_name"],
                            "relationship": relation})

        return results
