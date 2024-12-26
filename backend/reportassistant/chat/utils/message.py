from chat.models import Message, MessageType
from db_configurator.models import DatabaseSource
from reporter_agent.models import Chart
from reporter_agent.reporter.state import GraphState
from reporter_agent.reporter.subgraph.visualisation_agent.ai import RepType


def save_message_from_reporter(state: GraphState, data_source: DatabaseSource, conversation_id: int) -> Message:
    chart = Chart(
        data_source=data_source,
        title="title",
        description="description",
        type=state["representation_data"].type.value,
        sql_query=state["sql_query"],
        meta_data=state["representation_data"].to_dict() if state["representation_data"].type == RepType.CHART else None
    )
    chart.save()

    message = Message(
        conversation_id=conversation_id,
        type=MessageType.AI.value,
        message=state["representation_data"].data if state["representation_data"].type == RepType.TEXT else None,
        chart=chart,
    )
    message.save()
    return message
