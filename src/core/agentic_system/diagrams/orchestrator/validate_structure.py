import logging
from src.core.agentic_system.diagrams.orchestrator.consts import MAX_NODES, QUESTION_MARKERS

def validate_hierarchical_structure(nodes: list) -> bool:
    """Validate hierarchical node structure for correctness"""
    if not nodes:
        logging.error("No nodes provided for validation")
        return False

    node_ids = set()
    hierarchy_valid = True

    for node in nodes:
        # Validate node_id uniqueness
        if hasattr(node, "node_id"):
            if node.node_id in node_ids:
                logging.error(f"Duplicate node_id: {node.node_id}")
                hierarchy_valid = False
            node_ids.add(node.node_id)

        # Validate title is a question
        if hasattr(node, "title"):
            title = node.title.strip()
            if not any(title.startswith(marker) for marker in QUESTION_MARKERS):
                logging.warning(
                    f"Node {getattr(node, 'node_id', 'unknown')} title '{title}' is not a question"
                )
                hierarchy_valid = False
            if not title.endswith("?"):
                logging.warning(
                    f"Node {getattr(node, 'node_id', 'unknown')} title does not end with '?'"
                )
                hierarchy_valid = False

        # Validate hierarchy level
        if hasattr(node, "hierarchy_level"):
            if node.hierarchy_level < 0:
                logging.error(
                    f"Node {getattr(node, 'node_id', 'unknown')} has negative hierarchy_level"
                )
                hierarchy_valid = False
            # Root nodes (level 0) should not have parent
            if (
                node.hierarchy_level == 0
                and hasattr(node, "parent_node_id")
                and node.parent_node_id is not None
            ):
                logging.warning(
                    f"Root node {getattr(node, 'node_id', 'unknown')} has a parent"
                )

    # Validate parent-child relationships
    for node in nodes:
        if hasattr(node, "parent_node_id") and node.parent_node_id:
            if node.parent_node_id not in node_ids:
                logging.error(
                    f"Node {getattr(node, 'node_id', 'unknown')} references non-existent parent {node.parent_node_id}"
                )
                hierarchy_valid = False

        if hasattr(node, "children_node_ids"):
            for child_id in node.children_node_ids:
                if child_id not in node_ids:
                    logging.error(
                        f"Node {getattr(node, 'node_id', 'unknown')} references non-existent child {child_id}"
                    )
                    hierarchy_valid = False

    return hierarchy_valid


def validate_node_count(node_count: int) -> bool:
    """Validate that node count does not exceed MAX_NODES limit"""
    if node_count > MAX_NODES:
        logging.error(
            f"Node count {node_count} exceeds maximum limit of {MAX_NODES}. "
            f"Consider pruning the hierarchy or simplifying the decomposition."
        )
        return False
    if node_count == MAX_NODES:
        logging.info(f"Node count at maximum limit: {MAX_NODES} nodes")
    else:
        logging.info(f"Node count within limits: {node_count}/{MAX_NODES} nodes")
    return True
