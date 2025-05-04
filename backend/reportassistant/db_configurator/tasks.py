import enum
import os

import pandas as pd
from django.contrib.auth.models import User
from django_tasks import task
from django.utils.translation import gettext_noop
from sqlalchemy import create_engine

from common.db.manager.database_manager import DatabaseManager
from db_configurator.models import DatabaseSource, Status
from db_configurator.ai import cleaning_pandas_df
from dbloader.services import DBLoader
from home.models import Notification, Level

class LoadingMessage(enum.Enum):
    DATABASE_LOADED_SUCCESSFULLY= gettext_noop("DATABASE_LOADED_SUCCESSFULLY")
    ERROR_TO_LOAD_DATABASE = gettext_noop('ERROR_TO_LOAD_DATABASE')

@task()
def load_db(datasource_id: int, user_id: int):
    datasource = DatabaseSource.objects.get(id=datasource_id)
    user = User.objects.get(id=user_id)
    try:
        DBLoader(datasource).load()
        datasource.status = Status.READY.value
        if user:
            note = Notification(text=LoadingMessage.DATABASE_LOADED_SUCCESSFULLY.value, level=Level.SUCCESS.value, user=user)
            note.save()
        datasource.save()
    except Exception as e:
        datasource.status = Status.ERROR.value
        note = Notification(text=LoadingMessage.ERROR_TO_LOAD_DATABASE.value, level=Level.ERROR.value, user=user)
        note.save()
        datasource.save()
        raise e

@task()
def load_excel(datasource_id: int, user_id: int, files_dir: str):
    user = User.objects.get(id=user_id)
    datasource = DatabaseSource.objects.get(id=datasource_id)
    try:
        connection_string = f"{datasource.type}://{datasource.username}:{datasource.password}@{datasource.host}:{datasource.port}/{datasource.name}"
        engine = create_engine(connection_string)
        database_manager = DatabaseManager(db_source=datasource)

        schema = "schema_" + str(datasource.id)
        if not database_manager.check_schema_exists(schema):
            database_manager.create_schema(schema)
        datasource.schema_name = schema
        datasource.save()
        for filename in os.listdir(files_dir):
            file_path = os.path.join(files_dir, filename)
            if filename.lower().endswith('.xlsx'):
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                df = pd.read_csv(file_path)

            df = cleaning_pandas_df(df)

            table_name = os.path.splitext(filename)[0].lower().replace(".csv", "").replace(".xlsx", "")
            table_name = ''.join(c if c.isalnum() else '_' for c in table_name)
            df.to_sql(name=table_name, con=engine, index=False, if_exists='replace', schema=schema)

        load_db.enqueue(datasource_id, user_id)
    except Exception as e:
        datasource.status = Status.ERROR.value
        note = Notification(text=LoadingMessage.ERROR_TO_LOAD_DATABASE.value, level=Level.ERROR.value, user=user)
        note.save()
        datasource.save()
        raise e