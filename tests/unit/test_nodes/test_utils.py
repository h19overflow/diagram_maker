"""
Unit tests for node utils.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.core.agentic_system.nodes.utils import (
    populate_node_description,
    search_for_node,
    validate_query_relevance
)
from src.core.agentic_system.respone_formats import HierarchicalNodeTitle
from langchain_core.documents import Document


@pytest.fixture
def sample_node():
    """Create a sample HierarchicalNodeTitle for testing."""
    return HierarchicalNodeTitle(
        node_id="node_001",
        title="What is QLoRA?",
        hierarchy_level=0,
        parent_node_id=None,
        children_node_ids=[]
    )


@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    return [
        Document(page_content="QLoRA is a quantization technique", metadata={"source": "qlora.pdf"}),
        Document(page_content="It reduces memory usage", metadata={"source": "qlora.pdf"})
    ]


class TestPopulateNodeDescription:
    """Test cases for populate_node_description."""

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.invoke_agent')
    async def test_successful_population(self, mock_invoke, sample_node, sample_documents):
        """Test successful description population."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.response = "QLoRA is a quantization technique for fine-tuning"
        mock_invoke.return_value = {"structured_response": mock_response}

        # Execute
        result = await populate_node_description(sample_node, sample_documents)

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == "node_001"
        assert result[1] == "QLoRA is a quantization technique for fine-tuning"
        mock_invoke.assert_called_once_with(sample_node.title, sample_documents)

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.invoke_agent')
    async def test_agent_returns_none(self, mock_invoke, sample_node, sample_documents):
        """Test handling when agent returns None."""
        # Setup
        mock_invoke.return_value = None

        # Execute
        result = await populate_node_description(sample_node, sample_documents)

        # Assert
        assert result[0] == "node_001"
        assert result[1] == ""  # Empty description

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.invoke_agent')
    async def test_missing_structured_response(self, mock_invoke, sample_node, sample_documents):
        """Test handling when structured_response is missing."""
        # Setup
        mock_invoke.return_value = {"messages": []}  # No structured_response

        # Execute
        result = await populate_node_description(sample_node, sample_documents)

        # Assert
        assert result[0] == "node_001"
        assert result[1] == ""

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.invoke_agent')
    async def test_exception_handling(self, mock_invoke, sample_node, sample_documents):
        """Test that exceptions are caught and return empty description."""
        # Setup
        mock_invoke.side_effect = Exception("Agent error")

        # Execute
        result = await populate_node_description(sample_node, sample_documents)

        # Assert
        assert result[0] == "node_001"
        assert result[1] == ""

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.invoke_agent')
    async def test_empty_response_string(self, mock_invoke, sample_node, sample_documents):
        """Test handling of empty response string."""
        # Setup
        mock_response = MagicMock()
        mock_response.response = ""
        mock_invoke.return_value = {"structured_response": mock_response}

        # Execute
        result = await populate_node_description(sample_node, sample_documents)

        # Assert
        assert result[0] == "node_001"
        assert result[1] == ""


class TestSearchForNode:
    """Test cases for search_for_node."""

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.vector_store')
    async def test_successful_search(self, mock_vector_store, sample_node, sample_documents):
        """Test successful document search."""
        # Setup
        mock_vector_store.search = AsyncMock(return_value=sample_documents)

        # Execute
        result = await search_for_node(sample_node)

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == "What is QLoRA?"
        assert result[1] == sample_documents
        mock_vector_store.search.assert_called_once_with(query="What is QLoRA?", k=3)

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.vector_store')
    async def test_empty_search_results(self, mock_vector_store, sample_node):
        """Test handling of empty search results."""
        # Setup
        mock_vector_store.search = AsyncMock(return_value=[])

        # Execute
        result = await search_for_node(sample_node)

        # Assert
        assert result[0] == "What is QLoRA?"
        assert result[1] == []

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.vector_store')
    async def test_search_exception(self, mock_vector_store, sample_node):
        """Test handling of search exceptions."""
        # Setup
        mock_vector_store.search = AsyncMock(side_effect=Exception("Search failed"))

        # Execute
        result = await search_for_node(sample_node)

        # Assert
        assert result[0] == "What is QLoRA?"
        assert result[1] == []  # Empty list on error


class TestValidateQueryRelevance:
    """Test cases for validate_query_relevance."""

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.vector_store')
    @patch('src.core.agentic_system.nodes.utils.config')
    async def test_relevant_query(self, mock_config, mock_vector_store):
        """Test that relevant queries pass validation."""
        # Setup
        mock_config.RELEVANCE_THRESHOLD = 0.5
        mock_vector_store.search_with_scores = AsyncMock(return_value=[
            (Document(page_content="Test"), 0.8),
            (Document(page_content="Test 2"), 0.7)
        ])

        # Execute
        is_relevant, error_msg = await validate_query_relevance("Test query")

        # Assert
        assert is_relevant is True
        assert error_msg is None

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.vector_store')
    @patch('src.core.agentic_system.nodes.utils.config')
    async def test_low_relevance_query(self, mock_config, mock_vector_store):
        """Test that low relevance queries fail validation."""
        # Setup
        mock_config.RELEVANCE_THRESHOLD = 0.5
        mock_vector_store.search_with_scores = AsyncMock(return_value=[
            (Document(page_content="Test"), 0.3),
            (Document(page_content="Test 2"), 0.2)
        ])

        # Execute
        is_relevant, error_msg = await validate_query_relevance("Test query")

        # Assert
        assert is_relevant is False
        assert error_msg is not None
        assert "not sufficiently relevant" in error_msg

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.vector_store')
    async def test_no_documents_found(self, mock_vector_store):
        """Test handling when no documents are found."""
        # Setup
        mock_vector_store.search_with_scores = AsyncMock(return_value=[])

        # Execute
        is_relevant, error_msg = await validate_query_relevance("Test query")

        # Assert
        assert is_relevant is False
        assert error_msg is not None
        assert "No relevant documents found" in error_msg

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.vector_store')
    async def test_exception_handling(self, mock_vector_store):
        """Test that exceptions are caught and returned as error."""
        # Setup
        mock_vector_store.search_with_scores = AsyncMock(side_effect=Exception("Search error"))

        # Execute
        is_relevant, error_msg = await validate_query_relevance("Test query")

        # Assert
        assert is_relevant is False
        assert error_msg is not None
        assert "Error validating query relevance" in error_msg

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.utils.vector_store')
    @patch('src.core.agentic_system.nodes.utils.config')
    async def test_exact_threshold(self, mock_config, mock_vector_store):
        """Test query that exactly meets the threshold."""
        # Setup
        mock_config.RELEVANCE_THRESHOLD = 0.5
        mock_vector_store.search_with_scores = AsyncMock(return_value=[
            (Document(page_content="Test"), 0.5),
            (Document(page_content="Test 2"), 0.4)
        ])

        # Execute
        is_relevant, error_msg = await validate_query_relevance("Test query")

        # Assert
        assert is_relevant is True  # Should pass (>= threshold)
        assert error_msg is None

