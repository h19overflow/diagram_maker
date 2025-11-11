"""
Unit tests for diagram_sketch_node.
"""

import pytest
from unittest.mock import patch
from src.core.agentic_system.nodes.diagram_sketch_node import diagram_sketch_node
from src.core.agentic_system.graph_state import GraphState
from src.core.agentic_system.respone_formats import NodeTitles, HierarchicalNodeTitle


@pytest.fixture
def mock_node_titles():
    """Create a mock NodeTitles object."""
    return NodeTitles(
        nodes=[
            HierarchicalNodeTitle(
                node_id="node_001",
                title="What is QLoRA?",
                hierarchy_level=0,
                parent_node_id=None,
                children_node_ids=["node_002"]
            )
        ]
    )


@pytest.fixture
def sample_state():
    """Create a sample GraphState for testing."""
    return GraphState(user_input="What is QLoRA and how does it work?")


class TestDiagramSketchNode:
    """Test cases for diagram_sketch_node."""

    @patch('src.core.agentic_system.nodes.diagram_sketch_node.invoke_agent')
    @patch('src.core.agentic_system.nodes.diagram_sketch_node.validate_query_relevance')
    def test_successful_diagram_generation(self, mock_validate, mock_invoke, sample_state, mock_node_titles):
        """Test successful diagram skeleton generation."""
        # Setup mocks - validate_query_relevance is async, so we need to return a coroutine
        async def mock_validate_func(*args):
            return (True, None)
        mock_validate.side_effect = mock_validate_func
        mock_invoke.return_value = mock_node_titles

        # Execute
        result = diagram_sketch_node(sample_state)

        # Assert
        assert "error_message" not in result or result["error_message"] is None
        assert "diagram_skeleton" in result
        assert result["diagram_skeleton"] == mock_node_titles
        mock_validate.assert_called_once()
        mock_invoke.assert_called_once_with(sample_state.user_input)

    @patch('src.core.agentic_system.nodes.diagram_sketch_node.validate_query_relevance')
    def test_low_relevance_query(self, mock_validate, sample_state):
        """Test that low relevance queries return error."""
        # Setup mock - validate_query_relevance is async
        error_msg = "Query not relevant to documents"
        async def mock_validate_func(*args):
            return (False, error_msg)
        mock_validate.side_effect = mock_validate_func

        # Execute
        result = diagram_sketch_node(sample_state)

        # Assert
        assert "error_message" in result
        assert result["error_message"] == error_msg
        assert "diagram_skeleton" not in result

    @patch('src.core.agentic_system.nodes.diagram_sketch_node.invoke_agent')
    @patch('src.core.agentic_system.nodes.diagram_sketch_node.validate_query_relevance')
    def test_agent_returns_none(self, mock_validate, mock_invoke, sample_state):
        """Test handling when agent returns None."""
        # Setup mocks - validate_query_relevance is async
        async def mock_validate_func(*args):
            return (True, None)
        mock_validate.side_effect = mock_validate_func
        mock_invoke.return_value = None

        # Execute
        result = diagram_sketch_node(sample_state)

        # Assert
        assert "error_message" in result
        assert "Failed to generate diagram skeleton" in result["error_message"]

    @patch('src.core.agentic_system.nodes.diagram_sketch_node.validate_query_relevance')
    def test_dict_state_access(self, mock_validate):
        """Test that node handles dict state correctly."""
        # Setup - validate_query_relevance is async
        state_dict = {"user_input": "Test query"}
        error_msg = "Query not relevant"
        async def mock_validate_func(*args):
            return (False, error_msg)
        mock_validate.side_effect = mock_validate_func

        # Execute
        result = diagram_sketch_node(state_dict)

        # Assert
        assert "error_message" in result
        assert result["error_message"] == error_msg

    @patch('src.core.agentic_system.nodes.diagram_sketch_node.validate_query_relevance')
    def test_exception_handling(self, mock_validate, sample_state):
        """Test that exceptions are caught and returned as error messages."""
        # Setup mock to raise exception
        mock_validate.side_effect = Exception("Test exception")

        # Execute
        result = diagram_sketch_node(sample_state)

        # Assert
        assert "error_message" in result
        assert "Error in diagram sketch node" in result["error_message"]
        assert "Test exception" in result["error_message"]

    @patch('src.core.agentic_system.nodes.diagram_sketch_node.invoke_agent')
    @patch('src.core.agentic_system.nodes.diagram_sketch_node.validate_query_relevance')
    def test_empty_user_input(self, mock_validate, mock_invoke, mock_node_titles):
        """Test handling of empty user input."""
        # Setup - validate_query_relevance is async
        state = GraphState(user_input="")
        async def mock_validate_func(*args):
            return (True, None)
        mock_validate.side_effect = mock_validate_func
        mock_invoke.return_value = mock_node_titles

        # Execute
        result = diagram_sketch_node(state)

        # Assert
        assert "error_message" not in result or result["error_message"] is None
        assert "diagram_skeleton" in result

