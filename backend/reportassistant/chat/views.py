from django.shortcuts import render
from .models import Message
from .forms import MessageForm
from django.http import JsonResponse
import uuid

def chat_view(request):
    if 'conversation_id' not in request.session:
        request.session['conversation_id'] = str(uuid.uuid4())  # Start a new conversation if none exists

    conversation_id = request.session['conversation_id']

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['user_message'].lower()
            chart_data = None

            if user_message == "pie":
                system_response = 'Here is your pie chart!'
                chart_data = {
                    "type": "pie",
                    "labels": ["Apples", "Bananas", "Cherries"],
                    "datasets": [{
                        "data": [5, 7, 3],
                        "backgroundColor": [
                            "rgba(255, 99, 132, 0.6)",
                            "rgba(54, 162, 235, 0.6)",
                            "rgba(75, 192, 192, 0.6)"
                        ]
                    }],
                }

            elif user_message == "bar":
                system_response = 'Here is your bar chart!'
                chart_data = {
                    "type": "bar",
                    "labels": ["Apples", "Bananas", "Cherries"],
                    "datasets": [{
                        "label": "Fruits Count",
                        "data": [5, 7, 3],
                        "backgroundColor": [
                            "rgba(255, 99, 132, 0.6)",
                            "rgba(54, 162, 235, 0.6)",
                            "rgba(75, 192, 192, 0.6)"
                        ],
                        "borderColor": [
                            "rgba(255, 99, 132, 1)",
                            "rgba(54, 162, 235, 1)",
                            "rgba(75, 192, 192, 1)"
                        ],
                        "borderWidth": 1
                    }],
                    "options": {
                        "scales": {
                            "y": {"beginAtZero": True}
                        }
                    }
                }

            elif user_message == "line":
                system_response = 'Here is your line chart!'
                chart_data = {
                    "type": "line",
                    "labels": ["Apples", "Bananas", "Cherries"],
                    "datasets": [{
                        "label": "Fruit Trends",
                        "data": [5, 7, 3],
                        "borderColor": "rgba(75, 192, 192, 1)",
                        "backgroundColor": "rgba(75, 192, 192, 0.4)",
                        "fill": True
                    }]
                }

            elif user_message == "bubble":
                system_response = 'Here is your bubble chart!'
                chart_data = {
                    "type": "bubble",
                    "datasets": [{
                        "label": "Country Statistics",
                        "data": [
                            {"x": 40000, "y": 80, "r": 5},
                            {"x": 35000, "y": 78, "r": 10},
                            {"x": 30000, "y": 75, "r": 20},
                            {"x": 25000, "y": 72, "r": 30},
                            {"x": 20000, "y": 70, "r": 40}
                        ],
                        "backgroundColor": "rgba(255, 99, 132, 0.6)",
                        "borderColor": "rgba(255, 99, 132, 1)"
                    }]
                }

            elif user_message == "histogram":
                system_response = 'Here is your histogram chart!'
                chart_data = {
                    "type": "bar",
                    "labels": [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
                    "datasets": [{
                        "label": "Age Frequency",
                        "data": [5, 10, 20, 30, 40, 35, 30, 25, 15, 10, 5, 3, 2, 1, 1],
                        "backgroundColor": "rgba(75, 192, 192, 0.6)",
                        "borderColor": "rgba(75, 192, 192, 1)"
                    }]
                }

            elif user_message == "scatter":
                system_response = 'Here is your scatter chart!'
                chart_data = {
                    "type": "scatter",
                    "datasets": [{
                        "label": "Income vs Spending",
                        "data": [
                            {"x": 50000, "y": 40000},
                            {"x": 60000, "y": 45000},
                            {"x": 70000, "y": 50000},
                            {"x": 80000, "y": 55000},
                            {"x": 90000, "y": 60000}
                        ],
                        "backgroundColor": "rgba(255, 99, 132, 0.6)",
                        "borderColor": "rgba(255, 99, 132, 1)"
                    }]
                }

            else:
                system_response = "I can generate pie, bar, line, bubble, histogram, or scatter charts. Try asking for one!"
            
            # Save the message to the database
            Message.objects.create(
                user_message=form.cleaned_data['user_message'],
                system_response=system_response,
                conversation_id=conversation_id
            )

            # Fetch all messages for the current conversation
            messages = Message.objects.filter(conversation_id=conversation_id).order_by('-timestamp')
            return JsonResponse({
                'user_message': user_message,
                'system_response': system_response,
                'messages': [{'user_message': msg.user_message, 'system_response': msg.system_response} for msg in messages],
                'chart_data': chart_data
            })
    else:
        form = MessageForm()

    messages = Message.objects.filter(conversation_id=conversation_id).order_by('-timestamp')
    return render(request, 'chat/chat.html', {'form': form, 'messages': messages, 'conversation_id': conversation_id})


def clear_chat(request):
    if request.method == 'POST':
        request.session['conversation_id'] = str(uuid.uuid4())
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

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
def clear_chat(request):
    if request.method == 'POST':
        # Generate a new conversation ID and update the session
        request.session['conversation_id'] = str(uuid.uuid4())
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

def trial(request):
    return render(request, 'chat/trial.html')

def trial_simple(request):
    return render(request, 'chat/trial_simple.html')
