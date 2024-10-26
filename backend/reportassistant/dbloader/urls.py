from django.urls import path

from . import views

urlpatterns = [
    path("", views.loader, name="loader"),
    path('relation_graph/create', views.create_relation_graph, name="create_relation_graph"),
    path('relation_graph/clear', views.clear_relation_graph, name="clear_relation_graph"),
    path('relation_graph/get_neighbours', views.get_neighbours, name="get_neighbours"),
]
