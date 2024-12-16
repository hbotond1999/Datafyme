from django.urls import path

from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('slots/<int:dashboard_id>/', views.get_dashboard_slots, name='get_dashboard_slots'),
    path('dashboards/', views.get_dashboards, name='get_dashboards'),
    path('create_dashboard/', views.create_dashboard, name='create_dashboard'),
    path('update_dashboard/', views.update_dashboard_slots, name='update_dashboard_slots'),
]
