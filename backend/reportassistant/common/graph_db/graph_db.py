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

    def create_relation(self, table1, table2):
        with self.driver.session() as session:
            result = self._create_and_return_relation(table1, table2)
            print(f"Created relation between: {result['t1']}, {result['t2']}")

    def _create_and_return_relation(self, table1, table2):

        query = (
            "MERGE (t1:Table { name: $table1 }) "
            "MERGE (t2:Table { name: $table2 }) "
            "MERGE (t1)-[:RELATED_TO]->(t2) "
            "MERGE (t2)-[:RELATED_TO]->(t1) "
            "RETURN t1.name, t2.name"
        )

        try:
            record = self.driver.execute_query(query, table1=table1, table2=table2, database_=self.database,
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
            "MATCH (t:Table)-[]->(neighbour) "
            "WHERE t.name = $table "
            "RETURN neighbour.name AS name"
        )

        neighbours = self.driver.execute_query(query, table=table, database_=self.database,
                                               routing_=RoutingControl.READ,
                                               result_transformer_=lambda r: r.value("name"))
        return neighbours
