from django.contrib.auth import get_user_model
from django.db import models

from reporter_agent.models import Chart


# Create your models here.
class Dashboard(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2500)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


class DashboardSlot(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    chart = models.OneToOneField(Chart, on_delete=models.CASCADE)
    row_num = models.IntegerField()
    col_num = models.IntegerField()