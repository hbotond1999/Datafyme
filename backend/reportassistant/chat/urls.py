from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('history/', views.chat_history, name='chat_history'),
    path('clear_chat/', views.clear_chat, name='clear_chat'),
    path('trial/', views.trial, name='trial'),
    path('trial_simple/', views.trial_simple, name='trial_simple'),
    path('continue_conversation/<int:conversation_id>', views.continue_conversation, name='continue_conversation'),
    path('get_conversation_status/', views.get_conversation_status, name='get_conversation_status'),
]
