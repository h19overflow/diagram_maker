"""
Unit tests for hierarchy_builder module.
"""

import pytest
from src.core.agentic_system.nodes.mermaid_parsing.hierarchy_builder import (
    group_nodes_by_level,
    build_hierarchy_tree
)
from src.core.agentic_system.respone_formats import Nodes, Edges


@pytest.fixture
def sample_nodes():
    """Create sample Nodes object for testing."""
    return Nodes(
        id=["node_001", "node_002", "node_003"],
        title=["Root Node", "Child Node 1", "Child Node 2"],
        hierarchy_level=[0, 1, 1],
        parent_node_id=[None, "node_001", "node_001"],
        description=["Root description", "Child 1 description", "Child 2 description"]
    )


@pytest.fixture
def sample_edges():
    """Create sample Edges object for testing."""
    return Edges(
        source=["node_001", "node_001"],
        target=["node_002", "node_003"]
    )


class TestGroupNodesByLevel:
    """Test cases for group_nodes_by_level."""

    def test_grouping_by_level(self, sample_nodes):
        """Test that nodes are correctly grouped by hierarchy level."""
        result = group_nodes_by_level(sample_nodes)

        assert 0 in result
        assert 1 in result
        assert len(result[0]) == 1
        assert len(result[1]) == 2
        assert result[0][0][0] == "node_001"
        assert result[1][0][0] == "node_002"
        assert result[1][1][0] == "node_003"

    def test_node_tuples_structure(self, sample_nodes):
        """Test that grouped nodes are tuples with correct structure."""
        result = group_nodes_by_level(sample_nodes)

        for nodes in result.values():
            for node_tuple in nodes:
                assert isinstance(node_tuple, tuple)
                assert len(node_tuple) == 3
                node_id, title, description = node_tuple
                assert isinstance(node_id, str)
                assert isinstance(title, str)
                assert isinstance(description, str) or description is None

    def test_descriptions_included(self, sample_nodes):
        """Test that descriptions are included in grouped nodes."""
        result = group_nodes_by_level(sample_nodes)

        assert result[0][0][2] == "Root description"
        assert result[1][0][2] == "Child 1 description"

    def test_no_descriptions(self):
        """Test grouping when descriptions are None."""
        nodes = Nodes(
            id=["node_001"],
            title=["Test"],
            hierarchy_level=[0],
            parent_node_id=[None],
            description=None
        )

        result = group_nodes_by_level(nodes)

        assert result[0][0][2] is None

    def test_mismatched_list_lengths(self):
        """Test that mismatched list lengths raise ValueError."""
        nodes = Nodes(
            id=["node_001", "node_002"],
            title=["Test"],  # Only one title
            hierarchy_level=[0, 1],
            parent_node_id=[None, "node_001"]
        )

        with pytest.raises(ValueError, match="Mismatched list lengths"):
            group_nodes_by_level(nodes)

    def test_single_level(self):
        """Test grouping with single hierarchy level."""
        nodes = Nodes(
            id=["node_001", "node_002"],
            title=["Node 1", "Node 2"],
            hierarchy_level=[0, 0],
            parent_node_id=[None, None]
        )

        result = group_nodes_by_level(nodes)

        assert len(result) == 1
        assert 0 in result
        assert len(result[0]) == 2


class TestBuildHierarchyTree:
    """Test cases for build_hierarchy_tree."""

    def test_tree_from_edges(self, sample_nodes, sample_edges):
        """Test building tree from edges."""
        result = build_hierarchy_tree(sample_nodes, sample_edges)

        assert "node_001" in result
        assert "node_002" in result["node_001"]
        assert "node_003" in result["node_001"]

    def test_tree_from_parent_node_ids(self, sample_nodes):
        """Test building tree from parent_node_id relationships."""
        edges = Edges(source=[], target=[])
        result = build_hierarchy_tree(sample_nodes, edges)

        assert "node_001" in result
        assert "node_002" in result["node_001"]
        assert "node_003" in result["node_001"]

    def test_combined_edges_and_parents(self, sample_nodes, sample_edges):
        """Test that tree combines both edges and parent relationships."""
        result = build_hierarchy_tree(sample_nodes, sample_edges)

        # Should have both relationships
        assert "node_001" in result
        assert len(result["node_001"]) == 2

    def test_no_edges(self, sample_nodes):
        """Test building tree with no edges."""
        edges = Edges(source=[], target=[])
        result = build_hierarchy_tree(sample_nodes, edges)

        # Should still build from parent_node_id
        assert "node_001" in result

    def test_empty_nodes(self):
        """Test building tree with empty nodes."""
        nodes = Nodes(
            id=[],
            title=[],
            hierarchy_level=[],
            parent_node_id=[]
        )
        edges = Edges(source=[], target=[])

        result = build_hierarchy_tree(nodes, edges)

        assert result == {}

    def test_orphan_nodes(self):
        """Test handling of nodes without parents or edges."""
        nodes = Nodes(
            id=["node_001"],
            title=["Orphan"],
            hierarchy_level=[0],
            parent_node_id=[None]
        )
        edges = Edges(source=[], target=[])

        result = build_hierarchy_tree(nodes, edges)

        # Orphan node should not appear as a parent
        assert "node_001" not in result or len(result.get("node_001", [])) == 0

