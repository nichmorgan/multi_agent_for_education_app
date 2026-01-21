import os
import sys

import django
from neo4j import GraphDatabase

# Add project root to path
sys.path.append(os.getcwd())

# Setup Django to load settings (and thus env vars)
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "multi_agent_for_education_app.settings"
)
django.setup()

from django.conf import settings


def check_neo4j():
    uri = settings.NEO4J_URI
    user = settings.NEO4J_USERNAME
    password = settings.NEO4J_PASSWORD

    print(f"Testing connection to: {uri}")
    print(f"User: {user}")
    # Don't print password

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 'Connection Successful' AS message")
            record = result.single()
            print(f"Success: {record['message']}")
        driver.close()
    except Exception as e:
        print(f"Connection Failed: {e}")


if __name__ == "__main__":
    check_neo4j()
