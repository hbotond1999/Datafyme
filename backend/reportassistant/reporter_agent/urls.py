from django.urls import path

from . import views

urlpatterns = [
    path('sql_agent', views.sql_agent, name="sql_agent"),
]
