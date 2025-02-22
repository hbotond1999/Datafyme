from django_tasks import task

from chat.models import Conversation
from reporter_agent.reporter.agents import generate_title_agent


@task()
def generate_title(conversation_id: int, message: str, language: str):
    title = generate_title_agent().invoke({"first_message": message, "language": language})
    conversation = Conversation.objects.get(id=conversation_id)
    conversation.title = title
    conversation.save()