from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
import os
from ingest.tasks import process_upload


from ingest.models import IngestionTask

def upload_file(request):
    if request.method == "POST" and request.FILES["file"]:
        myfile = request.FILES["file"]
        fs = FileSystemStorage(location="media/uploads")
        filename = fs.save(myfile.name, myfile)
        uploaded_file_path = fs.path(filename)

        # Create IngestionTask
        task = IngestionTask.objects.create(file_name=filename)

        # Enqueue the processing task
        try:
            # Pass the task ID to the background task
            process_upload(uploaded_file_path, task.id)
            messages.success(
                request, f"File loaded successfully. Processing started for {filename}."
            )
        except Exception as e:
            task.status = IngestionTask.Status.FAILED
            task.save()
            messages.error(request, f"Error starting process: {e}")

        return redirect("upload_file")

    return render(request, "ingest/upload.html")


def task_list(request):
    tasks = IngestionTask.objects.all().order_by("-created_at")
    return render(request, "ingest/task_list.html", {"tasks": tasks})


def cancel_task(request, task_id):
    if request.method == "POST":
        try:
            task = IngestionTask.objects.get(id=task_id)
            if task.status in [IngestionTask.Status.PENDING, IngestionTask.Status.PROCESSING]:
                task.status = IngestionTask.Status.CANCELLED
                task.save()
                messages.success(request, f"Task {task.file_name} cancelled.")
            else:
                messages.warning(request, f"Task {task.file_name} cannot be cancelled.")
        except IngestionTask.DoesNotExist:
            messages.error(request, "Task not found.")
    return redirect("task_list")
