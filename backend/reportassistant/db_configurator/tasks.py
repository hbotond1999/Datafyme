import enum

from django.contrib.auth.models import User
from django_tasks import task
from django.utils.translation import gettext_noop

from db_configurator.models import DatabaseSource, Status
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
        raise e