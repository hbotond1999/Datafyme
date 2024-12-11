from django.db import models
import uuid

class Message(models.Model):
    user_message = models.TextField()
    system_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    conversation_id = models.UUIDField(default=uuid.uuid4, editable=False)  # Unique ID for each conversation

    def __str__(self):
        return f"User: {self.user_message}, Response: {self.system_response}, Conversation ID: {self.conversation_id}"
