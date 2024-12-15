from django.urls import path

from home import views

app_name= "home"

urlpatterns = [
    path('notifications', views.get_messages, name='get_notifications'),

]