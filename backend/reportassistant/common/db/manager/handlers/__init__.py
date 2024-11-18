from typing import Dict, Type

from db_configurator.models import DBType
from common.db.manager.abc import DatabaseManagerAbc

from common.db.manager.handlers.postgres import PostgresDatabaseManager

HANDLER: Dict[str, Type[DatabaseManagerAbc]] = {str(DBType.POSTGRESQL.value): PostgresDatabaseManager}

