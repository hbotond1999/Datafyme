from typing import Dict, Type

from db_configurator.models import DBType
from dbloader.services.utils.db_schema.abc import SchemaExtractor

from dbloader.services.utils.db_schema.handlers.postgres import PostgresSchemaExtractor

HANDLER: Dict[str, Type[SchemaExtractor]] = {str(DBType.POSTGRESQL.value): PostgresSchemaExtractor}

