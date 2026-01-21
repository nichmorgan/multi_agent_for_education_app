import asyncio
import json
import logging
from typing import AsyncGenerator

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect, render

from ingest.models import IngestionTask
from ingest.tasks import process_upload

logger = logging.getLogger(__name__)

# UI Configuration
STATUS_COLORS = {
    IngestionTask.Status.PENDING: "warning",
    IngestionTask.Status.PROCESSING: "info",
    IngestionTask.Status.COMPLETED: "success",
    IngestionTask.Status.FAILED: "error",
    IngestionTask.Status.CANCELLED: "ghost",
}

ACTIVE_STATUSES = [
    IngestionTask.Status.PENDING,
    IngestionTask.Status.PROCESSING,
]


def upload_file(request: HttpRequest) -> HttpResponse:
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

        return redirect("task_detail", task_id=task.id)

    return render(request, "ingest/upload.html")


def task_list(request: HttpRequest) -> HttpResponse:
    tasks = IngestionTask.objects.all().order_by("-created_at")
    return render(
        request,
        "ingest/task_list.html",
        {
            "tasks": tasks,
            "status_colors": json.dumps(STATUS_COLORS),
            "active_statuses": json.dumps(ACTIVE_STATUSES),
        },
    )


def task_detail(request: HttpRequest, task_id: int) -> HttpResponse | HttpResponse:
    try:
        task = IngestionTask.objects.get(id=task_id)
        steps = [
            {"value": step.value, "label": step.label} for step in IngestionTask.Step
        ]
        return render(
            request,
            "ingest/task_detail.html",
            {
                "task": task,
                "steps": steps,
                "status_colors": json.dumps(STATUS_COLORS),
                "active_statuses": json.dumps(ACTIVE_STATUSES),
            },
        )
    except IngestionTask.DoesNotExist:
        messages.error(request, "Task not found.")
        return redirect("task_list")


def cancel_task(request: HttpRequest, task_id: int) -> HttpResponse:
    if request.method == "POST":
        try:
            task = IngestionTask.objects.get(id=task_id)
            if task.status in [
                IngestionTask.Status.PENDING,
                IngestionTask.Status.PROCESSING,
            ]:
                task.status = IngestionTask.Status.CANCELLED
                task.save()
                messages.success(request, f"Task {task.file_name} cancelled.")
            else:
                messages.warning(request, f"Task {task.file_name} cannot be cancelled.")
        except IngestionTask.DoesNotExist:
            messages.error(request, "Task not found.")
    return redirect("task_list")


async def task_progress(request: HttpRequest, task_id: int) -> StreamingHttpResponse:
    """
    Server-Sent Events (SSE) stream for task progress.
    """

    async def event_stream() -> AsyncGenerator[str, None]:
        while True:
            try:
                # Use aget for async ORM access
                task = await IngestionTask.objects.aget(id=task_id)

                # Check if state has changed or send keep-alive
                current_data = {
                    "status": task.status,
                    "step": task.step,
                }

                # Yield data
                yield f"data: {json.dumps(current_data)}\n\n"

                # Stop stream if terminal state
                if task.status in [
                    IngestionTask.Status.COMPLETED,
                    IngestionTask.Status.FAILED,
                    IngestionTask.Status.CANCELLED,
                ]:
                    break

                await asyncio.sleep(1)

            except IngestionTask.DoesNotExist:
                error_data = {"error": "Task not found"}
                yield f"data: {json.dumps(error_data)}\n\n"
                break
            except Exception as e:
                logger.error(f"SSE Error for task {task_id}: {e}")
                break

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")
