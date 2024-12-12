from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('history/', views.chat_history, name='chat_history'),
    path('clear_chat/', views.clear_chat, name='clear_chat'),
    path('trial/', views.trial, name='trial'),
    path('trial_simple/', views.trial_simple, name='trial_simple')
]
