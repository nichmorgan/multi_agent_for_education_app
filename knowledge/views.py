from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse
from neo4j import GraphDatabase
from django.views.decorators.csrf import csrf_exempt
import json
import re
from typing import Any, Dict, List, Union
from django.conf import settings

# === Neo4j setup ===
# Ideally this should be in settings.py, but for the speed run we stick to direct config or simple env vars

# Initialize driver (simple singleton pattern for this view file)
driver = GraphDatabase.driver(
    settings.NEO4J_URI, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
)


def graph_view(request: HttpRequest) -> HttpResponse:
    """Renders the main graph page."""
    return render(request, "knowledge/graph.html")


def graph_root(request: HttpRequest) -> JsonResponse:
    """
    Returns a root node ("Central node") with top-level Concept nodes as children.
    This mimics the previous hierarchical structure for expandable D3 behavior.
    """
    with driver.session() as session:
        # Get top-level Concept nodes (no incoming HAS_CHILD)
        result = session.run(
            """
            MATCH (c:Concept)
            WHERE NOT (()-[:HAS_CHILD]->(c))
            RETURN c
        """
        )
        concept_nodes: List[Dict[str, Any]] = [dict(r["c"]) for r in result]

    # Build a pseudo-root node just like your previous JSON
    root: Dict[str, Any] = {
        "id": "root",
        "name": "Central node",
        "children": concept_nodes,
    }
    return JsonResponse(root)


def expand_node(request: HttpRequest, node_id: str) -> JsonResponse:
    """
    Expands a single node (Concept/Procedure/Assessment) by fetching its immediate children.
    This lets the D3 graph dynamically add new layers on click.
    """
    with driver.session() as session:
        results = session.run(
            """
            MATCH (n {id:$node_id})-[:HAS_CHILD|PROCEDURAL_FOR|ASSESSES]->(child)
            RETURN child
        """,
            node_id=node_id,
        )
        children: List[Dict[str, Any]] = [dict(r["child"]) for r in results]
    return JsonResponse(children, safe=False)


@csrf_exempt
def update_node(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        node: Dict[str, Any] = json.loads(request.body)
        props: Dict[str, Any] = {
            k: v for k, v in node.items() if k not in ["id", "children"]
        }

        # 🔧 Automatically fix "source" to link to the real uploaded file
        if "source" in props and isinstance(props["source"], str):
            match = re.search(r"([A-Za-z0-9_\-]+)\s*\[page", props["source"])
            if match:
                base_name = match.group(1).strip()
                props["source"] = f"{settings.STATIC_URL}uploads/{base_name}.pdf"

        with driver.session() as session:
            query = """
            MATCH (n {id: $id})
            SET n += $props
            RETURN n
            """
            session.run(query, id=node["id"], props=props)

        return JsonResponse({"status": "updated"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
