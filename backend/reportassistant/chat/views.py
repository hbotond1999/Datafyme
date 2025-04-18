import logging
import os
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Subquery
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.translation import get_language

from chat.forms import MessageForm
from chat.models import Conversation, Message, MessageType
from chat.utils.message import save_message_from_reporter
from reporter_agent.reporter.graph import create_reporter_graph
from reporter_agent.reporter.state import GraphState
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.utils import RefineLimitExceededError
from reporter_agent.reporter.utils import save_graph_png
from reporter_agent.task import generate_title


logger = logging.getLogger('reportassistant.custom')


@login_required
def chat_view(request):
    if 'conversation_id' not in request.session:
        conversation = Conversation(user=request.user)
        conversation.save()
        request.session['conversation_id'] = conversation.id

    conversation_id = request.session['conversation_id']

    if request.method == 'POST':
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                user_message = form.cleaned_data['user_message']
                datasource = form.cleaned_data['database_source']
                request.session["database_source_id"] = datasource.id
                messages = list(Message.objects.filter(conversation_id=conversation_id, conversation__user=request.user))

                if len(messages) == 0:
                    generate_title.enqueue(conversation_id, user_message, get_language())

                chat_hist = []
                q_and_a = {}

                for msg in messages[-int(os.getenv('HISTORY_LIMIT'))*2:]:
                    if msg.type == "HUMAN":
                        if q_and_a:
                            chat_hist.append(q_and_a)
                            q_and_a = {}

                        q_and_a["HUMAN"] = msg.message

                    elif msg.type == "AI":
                        if not q_and_a:
                            q_and_a["HUMAN"] = "MISSING_QUESTION"

                        if msg.chart:
                            q_and_a[
                                "AI"] = f"{msg.message} Chart type: {msg.chart.type}; Chart description: {msg.chart.description}; Chart sql_query: {msg.chart.sql_query}"
                            q_and_a["image"] = msg.chart.chart_img_url
                        else:
                            q_and_a["AI"] = msg.message

                        chat_hist.append(q_and_a)
                        q_and_a = {}

                if q_and_a:
                    chat_hist.append(q_and_a)

                Message(conversation_id=conversation_id, type=MessageType.HUMAN.value, message=user_message, chart=None).save()
                reporter_graph = create_reporter_graph()
                # save graph image:
                if int(os.getenv('DEBUG')) == 1:
                    save_graph_png(reporter_graph, name='reporter_graph')
                final_state: GraphState = reporter_graph.invoke(
                    {
                        "database_source": datasource,
                        "chat_history": chat_hist,
                        "question": user_message,
                        "refine_sql_recursive_limit": 3,
                        "refine_empty_result_recursive_limit": 3,
                        "language": get_language()
                     }
                )
                message = save_message_from_reporter(final_state, datasource, conversation_id)
                return JsonResponse({
                    "type": message.type,
                    "message": message.message,
                    "timestamp": message.timestamp,
                    "chart_id": message.chart_id if message.chart else None,
                }, status=200)
            except RefineLimitExceededError as e:
                sys_message = e.message

                Message.objects.create(
                    conversation_id=conversation_id,
                    type=MessageType.AI.value,
                    message=sys_message,
                    chart=None
                )
                return JsonResponse({
                    "type": MessageType.AI.value,
                    "message": sys_message,
                    "timestamp": datetime.now(),
                    "chart_id": None,
                }, status=200)
        else:
            return JsonResponse({"error": form.errors})
    else:
        form = MessageForm(user=request.user, database_source_id=request.session.get("database_source_id", None))

    messages = Message.objects.filter(conversation_id=conversation_id, conversation__user=request.user)
    continue_conversation_ = request.session.get('continue_conversation')
    request.session['continue_conversation'] = 0
    return render(request, 'chat/chat.html', {'form': form, 'messages': messages, 'conversation_id': conversation_id, 'continue_conversation': continue_conversation_})

@login_required
def clear_chat(request):
    if request.method == 'POST':
        request.session['conversation_id'] = None
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@login_required
def chat_history(request):
    """
    View to display the chat history, showing all conversations ordered by the most recent timestamp.
    """
    # Get distinct conversation IDs ordered by the most recent timestamp
    recent_conversations = (
        Message.objects
        .filter(conversation_id=OuterRef('id'))
        .order_by('-timestamp')
    )

    conversations = (
        Conversation.objects
        .annotate(latest_message_time=Subquery(recent_conversations.values('timestamp')[:1]))
        .filter(latest_message_time__isnull=False)
        .order_by('-latest_message_time')
    )

    history = [
        {
            'title': conversation.title,
            'conversation_id': conversation.id,
            'messages': Message.objects.filter(conversation_id=conversation.id).order_by('timestamp')
        }
        for conversation in conversations
    ]

    return render(request, 'chat/chat_history.html', {'history': history})

# New view to reset the conversation ID (without deleting from the DB)
@login_required
def clear_chat(request):
    if request.method == 'POST':
        if 'conversation_id' in request.session:
            messages = Message.objects.filter(conversation_id=request.session['conversation_id'], conversation__user=request.user)
            if messages and len(messages) > 0:
                conversation = Conversation(user=request.user)
                conversation.save()
                request.session['conversation_id'] = conversation.id
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)

@login_required
def trial(request):
    return render(request, 'chat/trial.html')

@login_required
def trial_simple(request):
    return render(request, 'chat/trial_simple.html')

@login_required()
def continue_conversation(request, conversation_id):
    request.session['conversation_id'] = conversation_id
    request.session['continue_conversation'] = 1
    return redirect('chat:chat')
