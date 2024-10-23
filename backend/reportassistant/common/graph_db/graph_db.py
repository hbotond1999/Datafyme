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
            "CREATE (t1:Table { name: $table1 }) "
            "CREATE (t2:Table { name: $table2 }) "
            "CREATE (t1)-[:RELATED_TO]->(t2) "
            "CREATE (t2)-[:RELATED_TO]->(t1) "
            "RETURN t1.name, t2.name"
        )
        try:
            record = self.driver.execute_query(query, table1=table1, table2=table2, database_=self.database,
                                               result_transformer_=lambda r: r.single(strict=True))
            return {"t1": record["t1.name"], "t2": record["t2.name"]}

        except (DriverError, Neo4jError) as exception:
            logging.error("%s raised an error: \n%s", query, exception)
            raise

    def find_table_neighbours(self, table):
        names = self._find_and_return_table_neighbours(table)
        for name in names:
            print(f"Neighbour of {table}: {name}")

    def _find_and_return_table_neighbours(self, table):
        query = (
            "MATCH (t:Table)-[]-(neighbour) "
            "WHERE t.name = $table "
            "RETURN neighbour.name AS name"
        )

        neighbours = self.driver.execute_query(query, table=table, database_=self.database,
                                               routing_=RoutingControl.READ,
                                               result_transformer_=lambda r: r.value("name"))
        return neighbours


if __name__ == "__main__":
    neo4j_instance = Neo4JInstance()

    # get postgres_relations:
    response = requests.get('http://127.0.0.1:8000/dbloader')

    if response.status_code == 200:
        data = response.json()
        relations = data.get('relations', [])
        table_foreign_pairs = []
        for relation in relations:
            if relation is not None:
                table_name = relation.get("table_name")
                foreign_table_name = relation.get("foreign_table_name")

                if table_name and foreign_table_name:
                    table_foreign_pairs.append({"table_name": table_name, "foreign_table_name": foreign_table_name})

        print(table_foreign_pairs)
    else:
        table_foreign_pairs = []
        print(f"DJANGO API ERROR: {response.status_code}")

    try:
        for table_pair in table_foreign_pairs:
            neo4j_instance.create_relation(table_pair["table_name"], table_pair["foreign_table_name"])

        neo4j_instance.find_table_neighbours(table_foreign_pairs[0]["table_name"])
    finally:
        neo4j_instance.close()
