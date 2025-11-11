"""
Unit tests for retrieval_node.
"""

import pytest
from unittest.mock import patch
from src.core.agentic_system.nodes.retrieval_node import (
    retrieval_node,
    retrieval_node_sync,
)
from src.core.agentic_system.graph_state import GraphState
from src.core.agentic_system.respone_formats import NodeTitles, HierarchicalNodeTitle
from langchain_core.documents import Document


@pytest.fixture
def sample_diagram_skeleton():
    """Create a sample diagram skeleton for testing."""
    return NodeTitles(
        nodes=[
            HierarchicalNodeTitle(
                node_id="node_001",
                title="What is QLoRA?",
                hierarchy_level=0,
                parent_node_id=None,
                children_node_ids=["node_002"],
            ),
            HierarchicalNodeTitle(
                node_id="node_002",
                title="How does fine-tuning work?",
                hierarchy_level=1,
                parent_node_id="node_001",
                children_node_ids=[],
            ),
        ]
    )


@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    return [
        Document(
            page_content="QLoRA is a quantization technique",
            metadata={"source": "qlora.pdf"},
        ),
        Document(
            page_content="Fine-tuning adapts models",
            metadata={"source": "finetuning.pdf"},
        ),
    ]


@pytest.fixture
def sample_state(sample_diagram_skeleton):
    """Create a sample GraphState for testing."""
    return GraphState(user_input="Test query", diagram_skeleton=sample_diagram_skeleton)


class TestRetrievalNode:
    """Test cases for retrieval_node."""

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.nodes.retrieval_node.search_for_node")
    async def test_successful_retrieval(
        self, mock_search, sample_state, sample_documents
    ):
        """Test successful document retrieval for all nodes."""
        # Setup mocks
        mock_search.side_effect = [
            ("What is QLoRA?", sample_documents),
            ("How does fine-tuning work?", sample_documents),
        ]

        # Execute
        result = await retrieval_node(sample_state)

        # Assert
        assert "error_message" not in result or result["error_message"] is None
        assert "context_docs" in result
        assert len(result["context_docs"]) == 2
        assert "What is QLoRA?" in result["context_docs"]
        assert "How does fine-tuning work?" in result["context_docs"]
        assert mock_search.call_count == 2

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.nodes.retrieval_node.search_for_node")
    async def test_empty_diagram_skeleton(self, mock_search):
        """Test handling of empty diagram skeleton."""
        # Setup
        state = GraphState(user_input="Test", diagram_skeleton=None)

        # Execute
        result = await retrieval_node(state)

        # Assert
        assert "error_message" in result
        assert "No diagram skeleton found" in result["error_message"]
        mock_search.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.nodes.retrieval_node.search_for_node")
    async def test_dict_skeleton_conversion(self, mock_search, sample_documents):
        """Test that dict skeleton is converted to NodeTitles."""
        # Setup
        skeleton_dict = {
            "nodes": [
                {
                    "node_id": "node_001",
                    "title": "Test title",
                    "hierarchy_level": 0,
                    "parent_node_id": None,
                    "children_node_ids": [],
                }
            ]
        }
        state = GraphState(user_input="Test", diagram_skeleton=skeleton_dict)
        mock_search.return_value = ("Test title", sample_documents)

        # Execute
        result = await retrieval_node(state)

        # Assert
        assert "error_message" not in result or result["error_message"] is None
        assert "context_docs" in result
        mock_search.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.nodes.retrieval_node.search_for_node")
    async def test_dict_state_access(
        self, mock_search, sample_documents, sample_diagram_skeleton
    ):
        """Test that node handles dict state correctly."""
        # Setup
        state_dict = {"user_input": "Test", "diagram_skeleton": sample_diagram_skeleton}
        mock_search.return_value = ("What is QLoRA?", sample_documents)

        # Execute
        result = await retrieval_node(state_dict)

        # Assert
        assert "context_docs" in result

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.nodes.retrieval_node.search_for_node")
    async def test_parallel_retrieval(
        self, mock_search, sample_state, sample_documents
    ):
        """Test that searches are executed in parallel."""
        # Setup
        call_order = []

        async def track_calls(*args, **kwargs):
            call_order.append(len(call_order))
            return ("Test", sample_documents)

        mock_search.side_effect = track_calls

        # Execute
        result = await retrieval_node(sample_state)

        # Assert
        assert len(call_order) == 2  # Both calls should execute
        assert mock_search.call_count == 2
        assert "context_docs" in result  # Ensure result is used

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.nodes.retrieval_node.search_for_node")
    async def test_exception_handling(self, mock_search, sample_state):
        """Test that exceptions are caught and returned as error messages."""
        # Setup
        mock_search.side_effect = Exception("Search failed")

        # Execute
        result = await retrieval_node(sample_state)

        # Assert
        assert "error_message" in result
        assert "Error in retrieval node" in result["error_message"]

    def test_retrieval_node_sync(self, sample_state, sample_documents):
        """Test the synchronous wrapper function."""
        with patch(
            "src.core.agentic_system.nodes.retrieval_node.search_for_node"
        ) as mock_search:
            mock_search.side_effect = [
                ("What is QLoRA?", sample_documents),
                ("How does fine-tuning work?", sample_documents),
            ]

            # Execute
            result = retrieval_node_sync(sample_state)

            # Assert
            assert "context_docs" in result
            assert len(result["context_docs"]) == 2

    def test_retrieval_node_sync_exception(self, sample_state):
        """Test sync wrapper handles exceptions."""
        with patch(
            "src.core.agentic_system.nodes.retrieval_node.search_for_node"
        ) as mock_search:
            mock_search.side_effect = Exception("Test error")

            # Execute
            result = retrieval_node_sync(sample_state)

            # Assert
            assert "error_message" in result
            assert "Error in retrieval node" in result["error_message"]
            assert result is not None  # Ensure result is used
