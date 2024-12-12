from django.urls import path
from . import views

app_name = 'db_configurator'  # Register the namespace

urlpatterns = [
    path('', views.manage_connections, name='manage_connections'),
    path('add_connection', views.add_connection, name='add_connection'),
    path('manage/delete/<int:pk>/', views.delete_database, name='delete_database'),
    path('manage/pause/<int:pk>/', views.pause_connection, name='pause_connection'),
]
