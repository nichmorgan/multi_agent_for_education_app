from ingest.enums import Step
from ingest.enums import Status
from django_huey import task
from ingest.services.parsers.dual_parser import parse_dualpath
from knowledge.services.loader import upload_graph
from ingest.models import IngestionTask
import logging
import json

logger = logging.getLogger(__name__)


@task()
def process_upload(file_path: str, ingestion_task_id: int):
    """
    Async task to parse a file and upload the resulting graph to Neo4j.
    """
    logger.info(f"Starting processing for {file_path}")
    
    try:
        task_instance = IngestionTask.objects.get(id=ingestion_task_id)
        
        # Check cancellation
        if task_instance.status == Status.CANCELLED:
            logger.info(f"Task {ingestion_task_id} cancelled before starting.")
            return

        # Update to Processing/Parsing
        task_instance.status = Status.PROCESSING
        task_instance.step = Step.PARSING
        task_instance.save()

        # 1. Parse the file to get JSON output path
        json_path = parse_dualpath(file_path)

        # Check cancellation after parsing
        task_instance.refresh_from_db()
        if task_instance.status == Status.CANCELLED:
             logger.info(f"Task {ingestion_task_id} cancelled after parsing.")
             return

        # Update to Uploading
        task_instance.step = Step.UPLOADING
        task_instance.save()

        # 2. Read the JSON data
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 3. Upload to Knowledge Graph
        upload_graph(data)

        # Update to Completed/Done
        task_instance.status = Status.COMPLETED
        task_instance.step = Step.DONE
        task_instance.save()

        logger.info(f"Successfully processed and uploaded {file_path}")

    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        try:
             task_instance = IngestionTask.objects.get(id=ingestion_task_id)
             task_instance.status = Status.FAILED
             task_instance.save()
        except Exception:
            pass # If DB update fails, we just log the original error
        raise e
