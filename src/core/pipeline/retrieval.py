"""Retrieval/search functionality for the RAG pipeline."""

from __future__ import annotations

from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from logging import getLogger, basicConfig, INFO

# Configure logging if not already configured
basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = getLogger(__name__)


class Retriever:
    """
    Handles retrieval/search operations on a vector store.

    This class separates search functionality from vector store management,
    providing a clean interface for querying documents.
    """

    def __init__(self, vector_store: Optional[FAISS] = None):
        """
        Initialize the retriever with a vector store.

        Args:
            vector_store: FAISS vector store instance. If None, must be set later via set_vector_store().
        """
        self.vector_store = vector_store
        if vector_store is None:
            logger.info("Retriever initialized without vector store (will need to be set later)")

    def set_vector_store(self, vector_store: FAISS):
        """
        Set or update the vector store for this retriever.

        Args:
            vector_store: FAISS vector store instance
        """
        self.vector_store = vector_store
        logger.info("Vector store set for retriever")

    async def search(self, query: str, k: int = 10) -> List[Document]:
        """
        Search for similar documents in the vector store.

        Args:
            query: Search query string
            k: Number of results to return

        Returns:
            List of Document objects
        """
        try:
            if self.vector_store is None:
                logger.warning("Vector store is empty, returning empty results")
                return []

            return await self.vector_store.asimilarity_search(
                query=query,
                k=k,
            )
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise e

    async def search_with_scores(self, query: str, k: int = 10) -> List[tuple[Document, float]]:
        """
        Search for similar documents with similarity scores.

        Args:
            query: Search query string
            k: Number of results to return

        Returns:
            List of tuples containing (Document, score) pairs.
            Scores are normalized similarity scores in the range [0, 1] (higher = more similar).
            FAISS returns distance scores, which are converted to similarity scores here.
        """
        try:
            if self.vector_store is None:
                logger.warning("Vector store is empty, returning empty results")
                return []

            # FAISS returns distance scores (lower = more similar)
            # For cosine similarity, distance = 1 - cosine_similarity
            results = await self.vector_store.asimilarity_search_with_score(
                query=query,
                k=k,
            )

            # Convert distance scores to similarity scores in [0, 1] range
            # Using 1 / (1 + distance) to ensure scores are always in [0, 1]
            # This works for both cosine distance and L2 distance
            normalized_results = [
                (doc, 1.0 / (1.0 + distance)) for doc, distance in results
            ]

            return normalized_results
        except Exception as e:
            logger.error(f"Error searching with scores: {e}")
            raise e

    def search_sync(self, query: str, k: int = 10) -> List[Document]:
        """
        Synchronous version of search for non-async contexts.

        Args:
            query: Search query string
            k: Number of results to return

        Returns:
            List of Document objects
        """
        try:
            if self.vector_store is None:
                logger.warning("Vector store is empty, returning empty results")
                return []

            return self.vector_store.similarity_search(
                query=query,
                k=k,
            )
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise e

    def search_with_scores_sync(self, query: str, k: int = 10) -> List[tuple[Document, float]]:
        """
        Synchronous version of search_with_scores for non-async contexts.

        Args:
            query: Search query string
            k: Number of results to return

        Returns:
            List of tuples containing (Document, score) pairs.
            Scores are normalized similarity scores in the range [0, 1] (higher = more similar).
        """
        try:
            if self.vector_store is None:
                logger.warning("Vector store is empty, returning empty results")
                return []

            # FAISS returns distance scores (lower = more similar)
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
            )

            # Convert distance scores to similarity scores in [0, 1] range
            normalized_results = [
                (doc, 1.0 / (1.0 + distance)) for doc, distance in results
            ]

            return normalized_results
        except Exception as e:
            logger.error(f"Error searching with scores: {e}")
            raise e

