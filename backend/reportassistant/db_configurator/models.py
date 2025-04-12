import enum

from django.contrib.auth.models import Group, User
from django.db import models

class DBType(enum.Enum):
    POSTGRESQL = 'postgresql'
    MSSQL = 'mssql'

class SourceType(enum.Enum):
    EXCEL = 'excel'
    DB = 'db'

class Status(enum.Enum):
    PAUSED = 'PAUSED'
    LOADING = 'LOADING'
    READY = 'READY'
    ERROR = 'ERROR'

class DatabaseSource(models.Model):
    DB_TYPES = [(t.value, t.value) for t in DBType]
    STATUS =  [(t.value, t.value) for t in Status]
    type = models.CharField(max_length=50, choices=DB_TYPES)
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=300)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    host = models.CharField(max_length=1000)
    port = models.IntegerField()
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS, default=Status.LOADING.value)
    schema_name=models.CharField(max_length=1000, null=True, default=None) # korlát hogy csak az adott sémát nézzük
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=1000, choices=[(t.value, t.value) for t in SourceType], default=SourceType.DB.value)

    class Meta:
        unique_together = ('host', 'port', 'name', 'schema_name')

class TableDocumentation(models.Model):
    database_source = models.ForeignKey(DatabaseSource, on_delete=models.CASCADE)
    schema_name = models.CharField(max_length=255)
    table_name = models.CharField(max_length=255)
    documentation = models.JSONField()

    class Meta:
        unique_together = ('database_source', 'schema_name', 'table_name')

    def to_dict(self):
        return {
            "schema_name": self.schema_name,
            "table_name": self.table_name,
            "documentation": self.documentation
        }
