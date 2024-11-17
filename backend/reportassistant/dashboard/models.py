from django.contrib.auth import get_user_model
from django.db import models

from reporter_agent.models import Chart


# Create your models here.
class Dashboard(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2500)
    user_id = models.IntegerField(get_user_model())


class DashboardSlot(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    dashboard_id = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    chart_id = models.OneToOneField(Chart, on_delete=models.CASCADE)
    row_num = models.IntegerField()
    col_num = models.IntegerField()