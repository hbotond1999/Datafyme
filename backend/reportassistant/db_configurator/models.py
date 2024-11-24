import enum

from django.db import models

class DBType(enum.Enum):
    POSTGRESQL = 'postgresql'
    MSSQL = 'mssql'

class DatabaseSource(models.Model):
    DB_TYPES = [(t.value, t.value) for t in DBType]

    type = models.CharField(max_length=50, choices=DB_TYPES)
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    host = models.CharField(max_length=1000)
    port = models.IntegerField()
