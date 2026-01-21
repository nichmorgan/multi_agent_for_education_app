import json
from typing import Any, Dict, List, Union

from django.conf import settings
from neo4j import GraphDatabase

# Initialize driver
driver = GraphDatabase.driver(
    settings.NEO4J_URI, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
)


def flatten_props(props: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to flatten nested dictionaries for Neo4j properties."""
    flat = {}
    for k, v in props.items():
        if isinstance(v, dict):
            for subk, subv in v.items():
                flat[f"{k}_{subk}"] = subv
        elif isinstance(v, list):
            if all(isinstance(i, (str, int, float, bool)) for i in v):
                flat[k] = v
            elif all(isinstance(i, dict) for i in v):
                flat[k] = [json.dumps(i, ensure_ascii=False) for i in v]
            else:
                flat[k] = str(v)
        else:
            flat[k] = v
    return flat


def create_nodes_and_relationships(
    tx, node: Dict[str, Any], parent_id: str = None
) -> None:
    node_id = node.get("id")
    if not node_id:
        return

    node_label = "Concept"
    if node_id.startswith("P"):
        node_label = "Procedure"
    elif node_id.startswith("A"):
        node_label = "Assessment"

    # Props to set on the node (exclude structural keys)
    props = flatten_props(
        {
            k: v
            for k, v in node.items()
            if k not in ["children", "connections", "question_prompts"]
        }
    )

    # Create/Merge the node
    tx.run(
        f"""
        MERGE (n:{node_label} {{id:$id}})
        SET n += $props
        """,
        id=node_id,
        props=props,
    )

    # Create Question nodes for Assessments
    if node_label == "Assessment" and "question_prompts" in node:
        for idx, q in enumerate(node["question_prompts"], start=1):
            q_text = q.get("question", "") if isinstance(q, dict) else str(q)
            q_id = f"{node_id}-Q{idx}"
            tx.run(
                """
                MERGE (q:Question {id:$qid})
                SET q.text = $text
                WITH q
                MATCH (a {id:$aid})
                MERGE (a)-[:HAS_QUESTION]->(q)
                """,
                qid=q_id,
                text=q_text,
                aid=node_id,
            )

    # Relationship to Parent
    if parent_id:
        # Determine relationship type based on node types if needed,
        # but generic HAS_CHILD is often enough for hierarchy.
        # Original code used: HAS_CHILD
        tx.run(
            """
            MATCH (p {id:$parent_id}), (c {id:$child_id})
            MERGE (p)-[:HAS_CHILD]->(c)
            """,
            parent_id=parent_id,
            child_id=node_id,
        )

    # Semantic Connections
    for conn in node.get("connections", []):
        tx.run(
            f"""
            MATCH (a {{id:$from_id}}), (b {{id:$to_id}})
            MERGE (a)-[:{conn["relation"]}]->(b)
            """,
            from_id=node_id,
            to_id=conn["to"],
        )

    # Recurse
    for child in node.get("children", []):
        create_nodes_and_relationships(tx, child, parent_id=node_id)


def upload_graph(graph_data: Dict[str, Any]) -> None:
    """Uploads the full graph dictionary to Neo4j."""
    with driver.session() as session:
        session.execute_write(create_nodes_and_relationships, graph_data)
