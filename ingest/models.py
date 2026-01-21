from django.db import models
from django.utils.translation import gettext_lazy as _


class IngestionTask(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")
        CANCELLED = "cancelled", _("Cancelled")

    class Step(models.TextChoices):
        QUEUED = "queued", _("Queued")
        PARSING = "parsing", _("Parsing")
        UPLOADING = "uploading", _("Uploading")
        DONE = "done", _("Done")

    file_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    step = models.CharField(
        max_length=20,
        choices=Step.choices,
        default=Step.QUEUED,
    )
    task_id = models.CharField(
        max_length=255, blank=True, null=True
    )  # Huey task ID (uuid)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file_name} ({self.status})"
