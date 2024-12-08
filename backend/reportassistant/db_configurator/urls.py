from django.urls import path
from . import views

app_name = 'db_configurator'  # Register the namespace

urlpatterns = [
    path('', views.establish_connections, name='establish_connections'),
    path('manage/', views.manage_connections, name='manage_connections'),
    path('manage/delete/<int:pk>/', views.delete_database, name='delete_database'),
    path('manage/pause/<int:pk>/', views.pause_connection, name='pause_connection'),
]
