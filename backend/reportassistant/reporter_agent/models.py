from django.db import models

from db_configurator.models import DatabaseSource
from reporter_agent.reporter.subgraph.visualisation_agent.chart import ChartTypes

TYPES = {c.name: c.value for c in ChartTypes}
TYPES["TABLE"] = "TABLE"

# Create your models here.
class Chart(models.Model):
    data_source = models.ForeignKey(DatabaseSource, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2500)
    type = models.CharField(max_length=100, choices=TYPES)
    sql_query = models.TextField()
    meta_data = models.JSONField()