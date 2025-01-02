from typing import List, Dict, Any

from langchain.chains.base import Chain

from dbloader.services.graph_loader.ai.relation_agent import find_relation_agent
from dbloader.services.graph_loader.ai.response import FoundRelations


class RelationFinder:
    table_ddls: List[Dict[str, Any]]
    relation_agent: Chain

    def __init__(self, table_ddls: List[Dict[str, Any]]):
        """
        :param table_ddls: List of table ddls.
        """
        self.table_ddls = table_ddls
        self.relation_agent = find_relation_agent()

    def find_relation(self) -> FoundRelations:
        """
        Returns all the found relations between tables with the help of table ddls.

        :return: List of found relations.
        """
        table_relations: FoundRelations = self.relation_agent.invoke({"table_ddls": self.table_ddls})
        return table_relations
