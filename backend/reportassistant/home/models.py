import enum

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_noop


# Create your models here.
class Level(enum.Enum):
    SUCCESS=gettext_noop('SUCCESS')
    INFO = gettext_noop('INFO')
    WARNING = gettext_noop('WARNING')
    ERROR = gettext_noop('ERROR')
    CRITICAL = gettext_noop('CRITICAL')



class Notification(models.Model):
    LEVELS = [(t.value, t.value) for t in Level]
    level = models.CharField(max_length=50, choices=LEVELS)
    text = models.TextField(max_length=2000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
