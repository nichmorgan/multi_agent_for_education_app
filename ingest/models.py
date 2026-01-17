from django.db import models
from .enums import Status, Step
from utils import enum_to_choices

class IngestionTask(models.Model):
    file_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=enum_to_choices(Status),
        default=Status.PENDING,
    )
    step = models.CharField(
        max_length=20,
        choices=enum_to_choices(Step),
        default=Step.QUEUED,
    )
    task_id = models.CharField(max_length=255, blank=True, null=True)  # Huey task ID (uuid)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.file_name} ({self.status})"
