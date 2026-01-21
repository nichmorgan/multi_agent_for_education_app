from django.urls import path

from . import views

urlpatterns = [
    path("upload/", views.upload_file, name="upload_file"),
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/<int:task_id>/", views.task_detail, name="task_detail"),
    path("tasks/<int:task_id>/cancel/", views.cancel_task, name="cancel_task"),
    path("tasks/<int:task_id>/progress/", views.task_progress, name="task_progress"),
    path("", views.upload_file, name="index"),
]
