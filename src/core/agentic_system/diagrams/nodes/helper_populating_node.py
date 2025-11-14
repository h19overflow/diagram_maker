from src.core.agentic_system.diagrams.nodes.utils import populate_node_description
from src.core.agentic_system.respone_formats import (
    Nodes,
    Edges,
    IRSDiagramResponse,
)
from src.api.schemas.enums import DiagramType
from logging import getLogger
import asyncio

logger = getLogger(__name__)


async def helper_populating_node_async(state) -> dict:
    """
    Helper populating node that generates descriptions for all nodes in parallel.
    Transforms diagram_skeleton into IRSDiagramResponse with populated descriptions.
    """
    try:
        # Handle both dict and GraphState object access
        diagram_skeleton = (
            state.get("diagram_skeleton")
            if isinstance(state, dict)
            else state.diagram_skeleton
        )
        context_docs = (
            state.get("context_docs") if isinstance(state, dict) else state.context_docs
        )
        user_input = (
            state.get("user_input") if isinstance(state, dict) else state.user_input
        )

        # Convert dict to NodeTitles if needed
        if isinstance(diagram_skeleton, dict):
            from src.core.agentic_system.respone_formats import NodeTitles

            diagram_skeleton = NodeTitles(**diagram_skeleton)

        # Validate required state
        if diagram_skeleton is None or not diagram_skeleton.nodes:
            logger.warning("No diagram skeleton or nodes found in state")
            return {"error_message": "No diagram skeleton found for helper population"}

        if context_docs is None:
            logger.warning("No context_docs found in state")
            return {"error_message": "No context documents found for helper population"}

        # Create parallel tasks for all nodes
        tasks = []
        for node in diagram_skeleton.nodes:
            # Get documents for this node's title
            documents = (
                context_docs.get(node.title, [])
                if isinstance(context_docs, dict)
                else (
                    context_docs.get(node.title, [])
                    if hasattr(context_docs, "get")
                    else []
                )
            )
            if not documents:
                logger.warning(f"No documents found for node title: {node.title}")

            # Create task for this node
            tasks.append(populate_node_description(node, documents))

        # Execute all tasks in parallel
        logger.info(f"Starting parallel description population for {len(tasks)} nodes")
        results = await asyncio.gather(*tasks)

        # Create mapping of node_id -> description
        description_map = {node_id: description for node_id, description in results}

        # Build Nodes object from HierarchicalNodeTitle list
        node_ids = []
        titles = []
        hierarchy_levels = []
        parent_node_ids = []
        descriptions = []

        for node in diagram_skeleton.nodes:
            node_ids.append(node.node_id)
            titles.append(node.title)
            hierarchy_levels.append(node.hierarchy_level)
            parent_node_ids.append(node.parent_node_id)
            descriptions.append(description_map.get(node.node_id, ""))

        nodes_obj = Nodes(
            id=node_ids,
            title=titles,
            hierarchy_level=hierarchy_levels,
            parent_node_id=parent_node_ids,
            description=descriptions,
        )

        # Build Edges from both parent_node_id and children_node_ids relationships
        edges_set = set()  # Use set to deduplicate edges

        for node in diagram_skeleton.nodes:
            # Add edges from parent_node_id (parent -> node)
            if node.parent_node_id is not None:
                edges_set.add((node.parent_node_id, node.node_id))

            # Add edges from children_node_ids (node -> child)
            for child_id in node.children_node_ids:
                edges_set.add((node.node_id, child_id))

        # Convert set to lists for Edges object
        edge_sources = [source for source, _ in edges_set]
        edge_targets = [target for _, target in edges_set]

        edges_obj = Edges(
            source=edge_sources,
            target=edge_targets,
            description=None,  # Edge descriptions can be added later if needed
        )

        # Create IRSDiagramResponse
        diagram_title = user_input if user_input else "Diagram"

        final_diagram = IRSDiagramResponse(
            diagram_type=DiagramType.concept,  # Placeholder, will be transformed manually later
            title=diagram_title,
            nodes=[nodes_obj],  # List containing single Nodes object
            edges=[edges_obj],  # List containing single Edges object
        )

        logger.info(
            f"Successfully populated diagram with {len(node_ids)} nodes and {len(edge_sources)} edges"
        )

        return {
            "final_diagram": final_diagram,
            "error_message": None,
        }
    except Exception as e:
        logger.error(f"Error in helper populating node: {e}")
        return {"error_message": f"Error in helper populating node: {e}"}


def helper_populating_node(state) -> dict:
    """
    Synchronous wrapper for the async helper populating node.
    """
    try:
        return asyncio.run(helper_populating_node_async(state))
    except Exception as e:
        logger.error(f"Error in helper populating node sync wrapper: {e}")
        return {"error_message": f"Error in helper populating node: {e}"}
