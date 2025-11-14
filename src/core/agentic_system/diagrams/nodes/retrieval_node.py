from src.core.agentic_system.diagrams.graph_state import GraphState
from src.core.agentic_system.diagrams.nodes.utils import search_for_node
from langchain_core.documents import Document
from typing import Dict, List
from logging import getLogger
import asyncio

logger = getLogger(__name__)


async def retrieval_node(state) -> dict:
    """
    Retrieval node that searches for documents for each node title in the diagram skeleton.
    Populates context_docs as a dictionary mapping node titles to their corresponding documents.
    All searches are performed in parallel for better performance.
    """
    try:
        # Handle both dict and GraphState object access
        diagram_skeleton = (
            state.get("diagram_skeleton")
            if isinstance(state, dict)
            else state.diagram_skeleton
        )

        # Convert dict to NodeTitles if needed
        if isinstance(diagram_skeleton, dict):
            from src.core.agentic_system.respone_formats import NodeTitles

            diagram_skeleton = NodeTitles(**diagram_skeleton)

        if diagram_skeleton is None or not diagram_skeleton.nodes:
            logger.warning("No diagram skeleton or nodes found in state")
            return {"error_message": "No diagram skeleton found for retrieval"}

        # Create tasks for all searches to run in parallel
        search_tasks = [search_for_node(node) for node in diagram_skeleton.nodes]

        # Execute all searches in parallel
        logger.info(f"Starting parallel retrieval for {len(search_tasks)} node titles")
        results = await asyncio.gather(*search_tasks)

        # Build dictionary from results
        context_docs_dict: Dict[str, List[Document]] = {
            title: documents for title, documents in results
        }

        logger.info(f"Retrieved documents for {len(context_docs_dict)} node titles")

        return {"context_docs": context_docs_dict, "error_message": None}
    except Exception as e:
        logger.error(f"Error in retrieval node: {e}")
        return {"error_message": f"Error in retrieval node: {e}"}


def retrieval_node_sync(state) -> dict:
    """
    Synchronous wrapper for the async retrieval node.
    """
    try:
        return asyncio.run(retrieval_node(state))
    except Exception as e:
        logger.error(f"Error in retrieval node sync wrapper: {e}")
        return {"error_message": f"Error in retrieval node: {e}"}


if __name__ == "__main__":
    from src.core.agentic_system.respone_formats import (
        NodeTitles,
        HierarchicalNodeTitle,
    )

    # Create a test state with diagram skeleton
    test_nodes = [
        HierarchicalNodeTitle(
            node_id="node_001",
            title="How is fine tuninng works?",
            hierarchy_level=0,
            parent_node_id=None,
            children_node_ids=["node_002", "node_003"],
        ),
        HierarchicalNodeTitle(
            node_id="node_002",
            title="What is Qlora and how it works?",
            hierarchy_level=1,
            parent_node_id="node_001",
            children_node_ids=[],
        ),
    ]

    test_skeleton = NodeTitles(nodes=test_nodes)
    state = GraphState(
        user_input="I want to create a diagram of the human body",
        diagram_skeleton=test_skeleton,
    )

    result = retrieval_node_sync(state)
    print(
        f"Retrieved documents for {len(result['context_docs']) if result['context_docs'] else 0} titles"
    )
    if result["context_docs"]:
        for title, docs in result["context_docs"].items():
            print(f"  {title}: {docs} documents")
