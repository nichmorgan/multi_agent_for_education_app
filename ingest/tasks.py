from django_huey import task
from ingest.services.parsers.dual_parser import parse_dualpath
from knowledge.services.loader import upload_graph
import logging
import json

logger = logging.getLogger(__name__)


@task()
def process_upload(file_path: str):
    """
    Async task to parse a file and upload the resulting graph to Neo4j.
    """
    logger.info(f"Starting processing for {file_path}")
    try:
        # 1. Parse the file to get JSON output path
        json_path = parse_dualpath(file_path)

        # 2. Read the JSON data
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 3. Upload to Knowledge Graph
        upload_graph(data)

        logger.info(f"Successfully processed and uploaded {file_path}")

    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        raise e
