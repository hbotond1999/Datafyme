from django.urls import path

from reporter_agent import views

app_name = "reporter_agent"

urlpatterns = [
    path('sql_agent', views.sql_agent, name="sql_agent"),
    path('chart/<int:chart_id>', views.get_chart, name="get_chart"),
    path('chart_description/', views.generate_description, name="generate_description"),
    path("chart_update/", views.edit_chart, name="edit_chart"),
    path('genai-models/', views.genai_model_list, name='genai_model_list'),
    path('genai-models/create/', views.genai_model_create, name='genai_model_create'),
    path('genai-models/edit/<int:model_id>/', views.genai_model_edit, name='genai_model_edit'),
    path('genai-models/delete/<int:model_id>/', views.genai_model_delete, name='genai_model_delete'),
    path('genai-models/test-api-key/', views.test_api_key, name='test_api_key'),
    path('chart/download/<int:chart_id>', views.download_chart, name='download_chart')
]
