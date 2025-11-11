"""
Unit tests for helper_populating_node.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.core.agentic_system.nodes.helper_populating_node import (
    helper_populating_node,
    helper_populating_node_async
)
from src.core.agentic_system.graph_state import GraphState
from src.core.agentic_system.respone_formats import (
    NodeTitles,
    HierarchicalNodeTitle,
    IRSDiagramResponse
)
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
                children_node_ids=["node_002"]
            ),
            HierarchicalNodeTitle(
                node_id="node_002",
                title="How does fine-tuning work?",
                hierarchy_level=1,
                parent_node_id="node_001",
                children_node_ids=[]
            )
        ]
    )


@pytest.fixture
def sample_context_docs():
    """Create sample context documents."""
    return {
        "What is QLoRA?": [
            Document(page_content="QLoRA is a quantization technique", metadata={})
        ],
        "How does fine-tuning work?": [
            Document(page_content="Fine-tuning adapts models", metadata={})
        ]
    }


@pytest.fixture
def sample_state(sample_diagram_skeleton, sample_context_docs):
    """Create a sample GraphState for testing."""
    return GraphState(
        user_input="Test query",
        diagram_skeleton=sample_diagram_skeleton,
        context_docs=sample_context_docs
    )


class TestHelperPopulatingNode:
    """Test cases for helper_populating_node."""

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.helper_populating_node.parse_to_flowchart')
    @patch('src.core.agentic_system.nodes.helper_populating_node.populate_node_description')
    async def test_successful_population(
        self,
        mock_populate,
        mock_mermaid,
        sample_state
    ):
        """Test successful node population and diagram generation."""
        # Setup mocks
        mock_populate.side_effect = [
            ("node_001", "QLoRA is a quantization technique"),
            ("node_002", "Fine-tuning adapts models")
        ]
        mock_mermaid.return_value = "flowchart TD\n    Node1[Test]"

        # Execute
        result = await helper_populating_node_async(sample_state)

        # Assert
        assert "error_message" not in result or result["error_message"] is None
        assert "final_diagram" in result
        assert "mermaid_diagram" in result
        assert isinstance(result["final_diagram"], IRSDiagramResponse)
        assert result["mermaid_diagram"] == "flowchart TD\n    Node1[Test]"
        assert mock_populate.call_count == 2
        mock_mermaid.assert_called_once()

    @pytest.mark.asyncio
    async def test_missing_diagram_skeleton(self):
        """Test handling of missing diagram skeleton."""
        # Setup
        state = GraphState(user_input="Test", diagram_skeleton=None)

        # Execute
        result = await helper_populating_node_async(state)

        # Assert
        assert "error_message" in result
        assert "No diagram skeleton found" in result["error_message"]

    @pytest.mark.asyncio
    async def test_missing_context_docs(self, sample_diagram_skeleton):
        """Test handling of missing context documents."""
        # Setup
        state = GraphState(
            user_input="Test",
            diagram_skeleton=sample_diagram_skeleton,
            context_docs=None
        )

        # Execute
        result = await helper_populating_node_async(state)

        # Assert
        assert "error_message" in result
        assert "No context documents found" in result["error_message"]

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.helper_populating_node.populate_node_description')
    async def test_dict_skeleton_conversion(self, mock_populate, sample_context_docs):
        """Test that dict skeleton is converted to NodeTitles."""
        # Setup
        skeleton_dict = {
            "nodes": [
                {
                    "node_id": "node_001",
                    "title": "Test title",
                    "hierarchy_level": 0,
                    "parent_node_id": None,
                    "children_node_ids": []
                }
            ]
        }
        state = GraphState(
            user_input="Test",
            diagram_skeleton=skeleton_dict,
            context_docs=sample_context_docs
        )
        mock_populate.return_value = ("node_001", "Description")

        # Execute
        result = await helper_populating_node_async(state)

        # Assert
        assert "error_message" not in result or result["error_message"] is None
        assert "final_diagram" in result

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.helper_populating_node.parse_to_flowchart')
    @patch('src.core.agentic_system.nodes.helper_populating_node.populate_node_description')
    async def test_edges_construction(
        self,
        mock_populate,
        mock_mermaid,
        sample_state
    ):
        """Test that edges are correctly constructed from parent and children."""
        # Setup
        mock_populate.side_effect = [
            ("node_001", "Description 1"),
            ("node_002", "Description 2")
        ]
        mock_mermaid.return_value = "flowchart TD"

        # Execute
        result = await helper_populating_node_async(sample_state)

        # Assert
        assert "final_diagram" in result
        diagram = result["final_diagram"]
        assert len(diagram.edges) > 0
        edges = diagram.edges[0]
        # Should have edge from node_001 to node_002
        edge_pairs = list(zip(edges.source, edges.target, strict=True))
        assert ("node_001", "node_002") in edge_pairs

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.helper_populating_node.parse_to_flowchart')
    @patch('src.core.agentic_system.nodes.helper_populating_node.populate_node_description')
    async def test_mermaid_parsing_failure(
        self,
        mock_populate,
        mock_mermaid,
        sample_state
    ):
        """Test handling of Mermaid parsing failure."""
        # Setup
        mock_populate.side_effect = [
            ("node_001", "Description 1"),
            ("node_002", "Description 2")
        ]
        mock_mermaid.side_effect = Exception("Mermaid parsing failed")

        # Execute
        result = await helper_populating_node_async(sample_state)

        # Assert
        assert "final_diagram" in result
        assert result["mermaid_diagram"] is None
        assert "error_message" not in result or result["error_message"] is None

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.helper_populating_node.populate_node_description')
    async def test_parallel_population(self, mock_populate, sample_state):
        """Test that node descriptions are populated in parallel."""
        # Setup
        call_order = []
        async def track_calls(*args, **kwargs):
            call_order.append(len(call_order))
            return (f"node_{len(call_order):03d}", "Description")
        
        mock_populate.side_effect = track_calls

        # Execute
        result = await helper_populating_node_async(sample_state)

        # Assert
        assert len(call_order) == 2  # Both calls should execute
        assert mock_populate.call_count == 2
        assert "final_diagram" in result  # Ensure result is used

    @pytest.mark.asyncio
    @patch('src.core.agentic_system.nodes.helper_populating_node.populate_node_description')
    async def test_exception_handling(self, mock_populate, sample_state):
        """Test that exceptions are caught and returned as error messages."""
        # Setup
        mock_populate.side_effect = Exception("Population failed")

        # Execute
        result = await helper_populating_node_async(sample_state)

        # Assert
        assert "error_message" in result
        assert "Error in helper populating node" in result["error_message"]

    @patch('src.core.agentic_system.nodes.helper_populating_node.helper_populating_node_async')
    def test_helper_populating_node_sync(self, mock_async, sample_state):
        """Test the synchronous wrapper function."""
        # Setup
        mock_async.return_value = {
            "final_diagram": MagicMock(),
            "mermaid_diagram": "flowchart TD",
            "error_message": None
        }

        # Execute
        result = helper_populating_node(sample_state)

        # Assert
        assert "final_diagram" in result
        mock_async.assert_called_once_with(sample_state)

    @patch('src.core.agentic_system.nodes.helper_populating_node.helper_populating_node_async')
    def test_helper_populating_node_sync_exception(self, mock_async, sample_state):
        """Test sync wrapper handles exceptions."""
        # Setup
        mock_async.side_effect = Exception("Test error")

        # Execute
        result = helper_populating_node(sample_state)

        # Assert
        assert "error_message" in result
        assert "Error in helper populating node" in result["error_message"]
        assert result is not None  # Ensure result is used

