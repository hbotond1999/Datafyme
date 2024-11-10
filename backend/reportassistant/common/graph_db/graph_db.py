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

    def create_relation(self, table_name, column_name, foreign_table_name, foreign_column_name):
        with self.driver.session() as session:
            result = self._create_and_return_relation(table_name, column_name, foreign_table_name, foreign_column_name)
            print(f"Created relation between: {result['t1']}, {result['t2']}")

    def _create_and_return_relation(self, table_name, column_name, foreign_table_name, foreign_column_name):

        query = (
            "MERGE (t1:Table { name: $table_name }) "
            "MERGE (t2:Table { name: $foreign_table_name }) "
            "MERGE (t1)-[r1:RELATED_TO { column_name: $column_name, foreign_column_name: $foreign_column_name }]->(t2)"
            "MERGE (t2)-[r2:RELATED_TO { column_name: $foreign_column_name, foreign_column_name: $column_name }]->(t1)"
            "RETURN t1.name, t2.name"
        )

        try:
            record = self.driver.execute_query(query, table_name=table_name, foreign_table_name=foreign_table_name,
                                               column_name=column_name, foreign_column_name=foreign_column_name,
                                               database_=self.database,
                                               result_transformer_=lambda r: r.single(strict=True))
            return {"t1": record["t1.name"], "t2": record["t2.name"]}

        except (DriverError, Neo4jError) as exception:
            logging.error("%s raised an error: \n%s", query, exception)
            raise

    def clear_graph_database(self):
        query = "MATCH (n) DETACH DELETE n"
        try:
            self.driver.execute_query(query, database_=self.database)
            logging.info("Az egész gráf adatbázis kiürítve.")

        except (DriverError, Neo4jError) as exception:
            logging.error("Hiba történt az adatbázis kiürítésekor: %s", exception)
            raise

    def find_table_neighbours(self, table):
        query = (
            "MATCH (t:Table)-[r:RELATED_TO]->(neighbour) "
            "WHERE t.name = $table "
            "RETURN neighbour.name AS name, r.column_name AS column_name, r.foreign_column_name AS foreign_column_name"
        )

        neighbours = self.driver.execute_query(query, table=table, database_=self.database,
                                               routing_=RoutingControl.READ,
                                               result_transformer_=lambda r: {"neighbour": r.value("name")})

        query = (
            "MATCH (t1:Table)-[r:RELATED_TO]->(t2:Table) "
            "WHERE t1.name = $table AND t2.name = $neighbour "
            "RETURN r.column_name AS column_name, r.foreign_column_name AS foreign_column_name"
        )

        results = []
        for neighbour in neighbours['neighbour']:
            records, summary, keys = self.driver.execute_query(query, table=table, neighbour=neighbour,
                                                               database_=self.database)
            relation = {
                'column_name': records[0]["column_name"],
                'foreign_column_name': records[0]["foreign_column_name"]
            }
            results.append({"neighbour": neighbour, "relationship": relation})

        return results
