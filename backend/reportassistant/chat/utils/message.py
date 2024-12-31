from chat.models import Message, MessageType
from db_configurator.models import DatabaseSource
from reporter_agent.models import Chart
from reporter_agent.reporter.state import GraphState
from reporter_agent.reporter.subgraph.visualisation_agent.ai import RepType


def save_message_from_reporter(state: GraphState, data_source: DatabaseSource, conversation_id: int) -> Message:
    chart = None
    message_str = None
    if state.get("representation_data", None):
        if state["representation_data"].type == RepType.TEXT:
            message_str = state["representation_data"].data
        else:
            chart = Chart(
                data_source=data_source,
                title=state["representation_data"].chart_title if state["representation_data"].type == RepType.CHART else None,
                description="description",
                type=state["representation_data"].chart_type.value if state["representation_data"].type == RepType.CHART else RepType.TABLE.value,
                sql_query=state["sql_query"],
                meta_data=state["representation_data"].data if state["representation_data"].type == RepType.CHART else None
            )
            chart.save()

    message = Message(
        conversation_id=conversation_id,
        type=MessageType.AI.value,
        message=message_str,
        chart=chart,
    )

    message.save()
    return message
