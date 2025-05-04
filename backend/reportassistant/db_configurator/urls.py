from django.urls import path
from . import views

app_name = 'db_configurator'  # Register the namespace

urlpatterns = [
    path('', views.manage_connections, name='manage_connections'),
    path('connection', views.connection, name='connection'),
    path('manage/delete/<int:pk>/', views.delete_database, name='delete_database'),
    path('manage/pause/<int:pk>/', views.pause_connection, name='pause_connection'),
    path('manage/user_databases/', views.get_user_databases, name='user_databases'),
    path("excel_to_database_source", views.excel_to_database_source, name="excel_to_database_source"),
]
