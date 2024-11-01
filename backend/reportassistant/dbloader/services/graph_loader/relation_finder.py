from typing import List

from langchain.chains.base import Chain

from dbloader.services.utils.db_schema.types import TablePreview
from dbloader.services.graph_loader.ai.relation_agent import find_relation_agent
from dbloader.services.graph_loader.ai.response import FoundRelations


class RelationFinder:
    table_previews: List[TablePreview]
    relation_agent: Chain

    def __init__(self, table_previews: List[TablePreview]):
        """
        :param table_previews: List of TablePreview objects containing the previews of each table.
        """
        self.table_previews = table_previews
        self.relation_agent = find_relation_agent()

    def find_relation(self) -> FoundRelations:
        """
        Returns all the found relations between tables with the help of previews.

        :return: List of found relations.
        """
        table_relations: FoundRelations = self.relation_agent.invoke({"table_previews": self.table_previews})
        return table_relations
