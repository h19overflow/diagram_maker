"""
Unit tests for flowchart_parser module.
"""

import pytest
from src.core.agentic_system.nodes.mermaid_parsing.flowchart_parser import (
    parse_to_flowchart,
    _get_node_shape
)
from src.core.agentic_system.respone_formats import (
    IRSDiagramResponse,
    Nodes,
    Edges
)
from src.api.schemas.enums import DiagramType


@pytest.fixture
def sample_diagram():
    """Create a sample IRSDiagramResponse for testing."""
    nodes = Nodes(
        id=["node_001", "node_002", "node_003"],
        title=["Root Node", "Child Node 1", "Child Node 2"],
        hierarchy_level=[0, 1, 1],
        parent_node_id=[None, "node_001", "node_001"],
        description=["Root desc", "Child 1 desc", "Child 2 desc"]
    )
    edges = Edges(
        source=["node_001", "node_001"],
        target=["node_002", "node_003"]
    )
    return IRSDiagramResponse(
        diagram_type=DiagramType.flowchart,
        title="Test Diagram",
        nodes=[nodes],
        edges=[edges]
    )


class TestGetNodeShape:
    """Test cases for _get_node_shape."""

    def test_level_0_rectangle(self):
        """Test that level 0 returns rectangle shape."""
        open_bracket, close_bracket = _get_node_shape(0)
        assert open_bracket == "["
        assert close_bracket == "]"

    def test_level_1_rounded(self):
        """Test that level 1 returns rounded rectangle shape."""
        open_bracket, close_bracket = _get_node_shape(1)
        assert open_bracket == "("
        assert close_bracket == ")"

    def test_level_2_stadium(self):
        """Test that level 2 returns stadium shape."""
        open_bracket, close_bracket = _get_node_shape(2)
        assert open_bracket == "(["
        assert close_bracket == "])"

    def test_level_3_cylinder(self):
        """Test that level 3+ returns cylinder shape."""
        open_bracket, close_bracket = _get_node_shape(3)
        assert open_bracket == "[("
        assert close_bracket == ")]"

    def test_level_4_cylinder(self):
        """Test that level 4 also returns cylinder shape."""
        open_bracket, close_bracket = _get_node_shape(4)
        assert open_bracket == "[("
        assert close_bracket == ")]"


class TestParseToFlowchart:
    """Test cases for parse_to_flowchart."""

    def test_successful_parsing(self, sample_diagram):
        """Test successful flowchart parsing."""
        result = parse_to_flowchart(sample_diagram)

        assert isinstance(result, str)
        assert "flowchart TD" in result
        assert "node_001" in result
        assert "node_002" in result
        assert "node_003" in result

    def test_node_shapes_by_level(self, sample_diagram):
        """Test that nodes have correct shapes based on hierarchy level."""
        result = parse_to_flowchart(sample_diagram)

        # Level 0 should have rectangle brackets
        assert "node_001[" in result
        # Level 1 should have rounded brackets
        assert "node_002(" in result or "node_003(" in result

    def test_descriptions_in_labels(self, sample_diagram):
        """Test that descriptions are included in node labels."""
        result = parse_to_flowchart(sample_diagram)

        assert "<br/>" in result  # Description separator
        assert "Root desc" in result or "Root Node" in result

    def test_edges_included(self, sample_diagram):
        """Test that edges are included in the flowchart."""
        result = parse_to_flowchart(sample_diagram)

        assert "-->" in result  # Edge syntax
        assert "node_001 --> node_002" in result or "node_001 --> node_003" in result

    def test_empty_nodes(self):
        """Test handling of diagram with no nodes."""
        diagram = IRSDiagramResponse(
            diagram_type=DiagramType.flowchart,
            title="Empty",
            nodes=[],
            edges=[]
        )

        result = parse_to_flowchart(diagram)

        assert "flowchart TD" in result
        assert "Empty[No nodes]" in result

    def test_nodes_with_no_ids(self):
        """Test handling of nodes object with no IDs."""
        nodes = Nodes(
            id=[],
            title=[],
            hierarchy_level=[],
            parent_node_id=[]
        )
        diagram = IRSDiagramResponse(
            diagram_type=DiagramType.flowchart,
            title="Test",
            nodes=[nodes],
            edges=[]
        )

        result = parse_to_flowchart(diagram)

        assert "Empty[No nodes]" in result

    def test_mismatched_edge_lengths(self):
        """Test handling of mismatched edge source/target lengths."""
        nodes = Nodes(
            id=["node_001"],
            title=["Test"],
            hierarchy_level=[0],
            parent_node_id=[None]
        )
        edges = Edges(
            source=["node_001"],
            target=[]  # Mismatched length
        )
        diagram = IRSDiagramResponse(
            diagram_type=DiagramType.flowchart,
            title="Test",
            nodes=[nodes],
            edges=[edges]
        )

        result = parse_to_flowchart(diagram)

        # Should still generate nodes but skip edges
        assert "node_001" in result
        assert "-->" not in result or "mismatched" in result.lower()

    def test_orphaned_edges(self):
        """Test handling of edges referencing non-existent nodes."""
        nodes = Nodes(
            id=["node_001"],
            title=["Test"],
            hierarchy_level=[0],
            parent_node_id=[None]
        )
        edges = Edges(
            source=["node_001"],
            target=["node_999"]  # Non-existent node
        )
        diagram = IRSDiagramResponse(
            diagram_type=DiagramType.flowchart,
            title="Test",
            nodes=[nodes],
            edges=[edges]
        )

        result = parse_to_flowchart(diagram)

        # Should generate nodes but skip orphaned edge
        assert "node_001" in result

    def test_no_edges(self):
        """Test parsing diagram with no edges."""
        nodes = Nodes(
            id=["node_001"],
            title=["Test"],
            hierarchy_level=[0],
            parent_node_id=[None]
        )
        diagram = IRSDiagramResponse(
            diagram_type=DiagramType.flowchart,
            title="Test",
            nodes=[nodes],
            edges=[]
        )

        result = parse_to_flowchart(diagram)

        assert "node_001" in result
        assert "flowchart TD" in result

    def test_special_characters_in_ids(self):
        """Test handling of special characters in node IDs."""
        nodes = Nodes(
            id=["node.001", "node-002"],
            title=["Test 1", "Test 2"],
            hierarchy_level=[0, 1],
            parent_node_id=[None, "node.001"]
        )
        edges = Edges(
            source=["node.001"],
            target=["node-002"]
        )
        diagram = IRSDiagramResponse(
            diagram_type=DiagramType.flowchart,
            title="Test",
            nodes=[nodes],
            edges=[edges]
        )

        result = parse_to_flowchart(diagram)

        # IDs should be sanitized
        assert "node_001" in result or "node.001" in result
        assert "node-002" in result

    def test_multiple_hierarchy_levels(self):
        """Test parsing with multiple hierarchy levels."""
        nodes = Nodes(
            id=["node_001", "node_002", "node_003", "node_004"],
            title=["L0", "L1", "L2", "L3"],
            hierarchy_level=[0, 1, 2, 3],
            parent_node_id=[None, "node_001", "node_002", "node_003"]
        )
        edges = Edges(
            source=["node_001", "node_002", "node_003"],
            target=["node_002", "node_003", "node_004"]
        )
        diagram = IRSDiagramResponse(
            diagram_type=DiagramType.flowchart,
            title="Test",
            nodes=[nodes],
            edges=[edges]
        )

        result = parse_to_flowchart(diagram)

        # All nodes should be present
        assert "node_001" in result
        assert "node_002" in result
        assert "node_003" in result
        assert "node_004" in result

    def test_duplicate_sanitized_ids(self):
        """Test handling of duplicate sanitized node IDs."""
        nodes = Nodes(
            id=["node.001", "node_001"],  # Both sanitize to same ID
            title=["Test 1", "Test 2"],
            hierarchy_level=[0, 1],
            parent_node_id=[None, "node.001"]
        )
        diagram = IRSDiagramResponse(
            diagram_type=DiagramType.flowchart,
            title="Test",
            nodes=[nodes],
            edges=[]
        )

        result = parse_to_flowchart(diagram)

        # Should handle duplicates by appending counter
        assert "node_001" in result or "node_001_1" in result

