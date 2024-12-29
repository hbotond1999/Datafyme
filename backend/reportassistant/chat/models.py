import enum
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_noop

from reporter_agent.models import Chart


class MessageType(enum.Enum):
    AI = gettext_noop('AI')
    HUMAN = gettext_noop('HUMAN')

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Message(models.Model):
    TYPES = [(t.value, t.value) for t in MessageType]
    conversation = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE
    )
    type = models.CharField(max_length=11, choices=TYPES)
    message = models.TextField(null=True, blank=True)
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

