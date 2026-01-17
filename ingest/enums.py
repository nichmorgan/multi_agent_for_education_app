from enum import StrEnum

class Status(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Step(StrEnum):
    QUEUED = "queued"
    PARSING = "parsing"
    UPLOADING = "uploading"
    DONE = "done"