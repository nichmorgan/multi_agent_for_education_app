from django.urls import path

from . import views

urlpatterns = [
    path("graph/", views.graph_view, name="graph_view"),
    path("graph-root/", views.graph_root, name="graph_root"),
    path("expand-node/<str:node_id>", views.expand_node, name="expand_node"),
    path("update_node/", views.update_node, name="update_node"),
]
