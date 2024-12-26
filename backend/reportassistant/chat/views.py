from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
import uuid

from chat.forms import MessageForm
from chat.models import Conversation, Message, MessageType
from chat.utils.message import save_message_from_reporter
from reporter_agent.reporter.graph import create_reporter_graph
from reporter_agent.reporter.state import GraphState


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
            user_message = form.cleaned_data['user_message']
            datasource = form.cleaned_data['database_source']
            messages = Message.objects.filter(conversation_id=conversation_id, conversation__user=request.user)
            chat_hist =[msg.type + ": " + (msg.message if msg.message else "") for msg in messages]
            Message(conversation_id=conversation_id, type=MessageType.HUMAN.value, message=user_message,chart=None).save()
            reporter_graph = create_reporter_graph()
            final_state: GraphState = reporter_graph.invoke(
                {"database_source": datasource, "chat_history": chat_hist, "question": user_message}
            )
            message = save_message_from_reporter(final_state, datasource, conversation_id)
            return JsonResponse({
                "type": message.type,
                "message": message.message,
                "timestamp": message.timestamp,
                "chart_id": message.chart_id if message.chart else None,
            }, status=200)
        else:
            return JsonResponse({"error": form.errors})
    else:
        form = MessageForm(user=request.user)

    messages = Message.objects.filter(conversation_id=conversation_id, conversation__user=request.user)
    return render(request, 'chat/chat.html', {'form': form, 'messages': messages, 'conversation_id': conversation_id})

@login_required
def clear_chat(request):
    if request.method == 'POST':
        request.session['conversation_id'] = None
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@login_required
def chat_history(request):
    # Get all conversations ordered by the most recent first
    conversations = Message.objects.values('conversation_id').distinct().order_by('-timestamp')
    history = []
    for conversation in conversations:
        messages = Message.objects.filter(conversation_id=conversation['conversation_id']).order_by('timestamp')
        history.append({
            'conversation_id': conversation['conversation_id'],
            'messages': messages
        })
    return render(request, 'chat/chat_history.html', {'history': history})

# New view to reset the conversation ID (without deleting from the DB)
@login_required
def clear_chat(request):
    if request.method == 'POST':
        # Generate a new conversation ID and update the session
        request.session['conversation_id'] = str(uuid.uuid4())
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@login_required
def trial(request):
    return render(request, 'chat/trial.html')

@login_required
def trial_simple(request):
    return render(request, 'chat/trial_simple.html')
