from django.urls import path

from reporter_agent import views

app_name = "reporter_agent"

urlpatterns = [
    path('sql_agent', views.sql_agent, name="sql_agent"),
    path('chart/<int:chart_id>', views.get_chart, name="get_chart"),
    path('chart_description', views.generate_description, name="generate_description"),
    path("chart_update/", views.edit_chart, name="edit_chart"),
]
