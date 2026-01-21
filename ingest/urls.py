from django.urls import path

from . import views

urlpatterns = [
    path("upload/", views.upload_file, name="upload_file"),
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/<int:task_id>/cancel/", views.cancel_task, name="cancel_task"),
    path("", views.upload_file, name="index"),
]
