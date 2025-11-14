"""
Utility functions for node operations.
"""

from src.core.agentic_system.diagrams.helpers.helper_agent import invoke_agent
from src.core.agentic_system.respone_formats import HierarchicalNodeTitle
from langchain_core.documents import Document
from src.core.pipeline.vector_store import vector_store
from src.core.pipeline.retrieval import Retriever
from src.configs.rag_config import RAGConfig
from typing import List, Tuple, Optional
from logging import getLogger
import asyncio

logger = getLogger(__name__)
config = RAGConfig()

# Initialize retriever - will be updated when vector store is loaded
_retriever_instance: Optional[Retriever] = None


def get_retriever() -> Retriever:
    """
    Get or create the retriever instance, ensuring it's initialized with the current vector store.

    Returns:
        Retriever instance
    """
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever(vector_store.vector_store)
    elif _retriever_instance.vector_store != vector_store.vector_store:
        # Update retriever if vector store has changed
        _retriever_instance.set_vector_store(vector_store.vector_store)
    return _retriever_instance


# Convenience: Create instance on module import
retriever = get_retriever()


async def populate_node_description(
    node: HierarchicalNodeTitle,
    documents: List[Document],
) -> tuple[str, str]:
    """
    Populate description for a single node using the helper agent.

    Args:
        node: HierarchicalNodeTitle node to populate
        documents: List of documents retrieved for this node's title

    Returns:
        Tuple of (node_id, description) where description comes from HelperResponse.response
    """
    try:
        logger.info(f"Populating description for node: {node.node_id} - {node.title}")

        # Call helper agent with node title and documents in thread pool for true parallelism
        loop = asyncio.get_event_loop()
        helper_response = await loop.run_in_executor(
            None, invoke_agent, node.title, documents
        )

        if helper_response is None:
            logger.warning(f"Helper agent returned None for node {node.node_id}")
            return (node.node_id, "")

        # First, extract structured_response if helper_response is a dict
        # (create_agent returns dict with 'structured_response' key)
        if isinstance(helper_response, dict):
            structured_response = helper_response.get("structured_response")
            if structured_response is None:
                logger.warning(
                    f"No structured_response in helper response dict for node {node.node_id}"
                )
                return (node.node_id, "")
            helper_response = structured_response

        # Extract description from HelperResponse object
        if hasattr(helper_response, "response"):
            description = helper_response.response if helper_response.response else ""
        else:
            logger.warning(
                f"Unexpected helper response type for node {node.node_id}: {type(helper_response)}"
            )
            description = ""

        return (node.node_id, description)
    except Exception as e:
        logger.error(f"Error populating description for node {node.node_id}: {e}")
        return (node.node_id, "")


async def search_for_node(node: HierarchicalNodeTitle) -> tuple[str, List[Document]]:
    """
    Search for documents for a single node title.

    Args:
        node: HierarchicalNodeTitle node to search documents for

    Returns:
        Tuple of (title, documents) where documents is a list of retrieved Document objects
    """
    title = node.title
    logger.info(f"Searching for documents with query: {title}")

    try:
        # Use sync search wrapped in executor to avoid event loop issues
        retriever = get_retriever()
        loop = asyncio.get_event_loop()
        documents = await loop.run_in_executor(
            None, retriever.search_sync, title, 3
        )
        logger.info(f"Found {len(documents)} documents for title: {title}")
        return (title, documents)
    except Exception as e:
        logger.error(f"Error searching for title '{title}': {e}")
        return (title, [])  # Empty list on error


async def validate_query_relevance(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if a query is relevant to the documents in the vector store.

    Args:
        query: The user's query string

    Returns:
        Tuple of (is_relevant, error_message)
        - is_relevant: True if query passes relevance check, False otherwise
        - error_message: Error message if not relevant, None if relevant
    """
    try:
        # Use sync search wrapped in executor to avoid event loop issues
        retriever = get_retriever()
        loop = asyncio.get_event_loop()
        results_with_scores = await loop.run_in_executor(
            None, retriever.search_with_scores_sync, query, 10
        )

        if len(results_with_scores) == 0:
            logger.warning(f"No documents found for query: {query}")
            return (
                False,
                "No relevant documents found. Please ensure documents are uploaded and the query is related to the document content.",
            )

        # Extract scores (second element of each tuple)
        scores = [score for _, score in results_with_scores]

        # Check the highest score (most relevant document)
        max_score = max(scores) if scores else 0.0
        avg_score = sum(scores) / len(scores) if scores else 0.0

        logger.info(
            f"Query relevance check - Max score: {max_score:.3f}, Avg score: {avg_score:.3f}, Threshold: {config.RELEVANCE_THRESHOLD}"
        )

        # Check if relevance is too low
        if max_score < config.RELEVANCE_THRESHOLD:
            logger.warning(
                f"Query '{query}' has low relevance (max score: {max_score:.3f} < threshold: {config.RELEVANCE_THRESHOLD})"
            )
            return (
                False,
                (
                    "The question is not sufficiently relevant to the documents in the knowledge base. "
                    "Please rephrase your question to better match the document content, or upload relevant documents."
                ),
            )

        # Query is relevant
        logger.info("Query passed relevance check")
        return (True, None)
    except Exception as e:
        logger.error(f"Error validating query relevance: {e}")
        return (False, f"Error validating query relevance: {e}")
