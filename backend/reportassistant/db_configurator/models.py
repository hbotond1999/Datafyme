import enum

from django.contrib.auth.models import Group
from django.db import models

class DBType(enum.Enum):
    POSTGRESQL = 'postgresql'
    MSSQL = 'mssql'

class DatabaseSource(models.Model):
    DB_TYPES = [(t.value, t.value) for t in DBType]

    type = models.CharField(max_length=50, choices=DB_TYPES)
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=300)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    host = models.CharField(max_length=1000)
    port = models.IntegerField()
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    is_paused = models.BooleanField(default=False) 

    class Meta:
        unique_together = ('host', 'port', 'name')