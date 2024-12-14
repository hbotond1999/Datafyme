from django_tasks import task

from db_configurator.models import DatabaseSource, Status
from dbloader.services import DBLoader


@task()
def load_db(datasource_id: int):
    datasource = DatabaseSource.objects.get(id=datasource_id)
    try:
        DBLoader(datasource).load()
        datasource.status = Status.READY.value
        datasource.save()
    except Exception as e:
        datasource.status = Status.ERROR.value
        raise e