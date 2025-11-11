"""
Unit tests for node_formatter module.
"""

from src.core.agentic_system.nodes.mermaid_parsing.node_formatter import (
    sanitize_node_id,
    escape_mermaid_text,
    format_node_label,
)


class TestSanitizeNodeId:
    """Test cases for sanitize_node_id."""

    def test_simple_node_id(self):
        """Test sanitization of simple node ID."""
        assert sanitize_node_id("node_001") == "node_001"

    def test_node_id_with_dots(self):
        """Test sanitization of node ID with dots."""
        assert sanitize_node_id("node.1.2") == "node_1_2"

    def test_node_id_with_special_chars(self):
        """Test sanitization of node ID with special characters."""
        # Trailing underscores are stripped, so "Node (1)" becomes "Node_1"
        assert sanitize_node_id("Node (1)") == "Node_1"

    def test_node_id_with_spaces(self):
        """Test sanitization of node ID with spaces."""
        assert sanitize_node_id("node 1") == "node_1"

    def test_node_id_with_hyphens(self):
        """Test that hyphens are preserved."""
        assert sanitize_node_id("node-1") == "node-1"

    def test_node_id_with_underscores(self):
        """Test that underscores are preserved."""
        assert sanitize_node_id("node_1") == "node_1"

    def test_consecutive_underscores(self):
        """Test that consecutive underscores are collapsed."""
        assert sanitize_node_id("node___1") == "node_1"

    def test_leading_trailing_underscores(self):
        """Test that leading/trailing underscores are removed."""
        assert sanitize_node_id("_node_1_") == "node_1"

    def test_empty_node_id(self):
        """Test that empty node ID returns default."""
        assert sanitize_node_id("") == "node"

    def test_only_special_chars(self):
        """Test node ID with only special characters."""
        assert sanitize_node_id("!!!") == "node"


class TestEscapeMermaidText:
    """Test cases for escape_mermaid_text."""

    def test_simple_text(self):
        """Test escaping of simple text."""
        assert escape_mermaid_text("Simple text") == "Simple text"

    def test_ampersand_escaping(self):
        """Test that ampersands are escaped."""
        assert escape_mermaid_text("A & B") == "A &amp; B"

    def test_less_than_escaping(self):
        """Test that less than signs are escaped."""
        assert escape_mermaid_text("A < B") == "A &lt; B"

    def test_greater_than_escaping(self):
        """Test that greater than signs are escaped."""
        assert escape_mermaid_text("A > B") == "A &gt; B"

    def test_quote_escaping(self):
        """Test that quotes are escaped."""
        assert escape_mermaid_text('Text "quoted"') == "Text &quot;quoted&quot;"

    def test_single_quote_escaping(self):
        """Test that single quotes are escaped."""
        assert escape_mermaid_text("Text 'quoted'") == "Text &#39;quoted&#39;"

    def test_multiple_special_chars(self):
        """Test escaping of multiple special characters."""
        result = escape_mermaid_text('A & B < C > D "E"')
        assert "&amp;" in result
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&quot;" in result

    def test_empty_text(self):
        """Test that empty text returns empty string."""
        assert escape_mermaid_text("") == ""

    def test_none_text(self):
        """Test that None text returns empty string."""
        assert escape_mermaid_text(None) == ""


class TestFormatNodeLabel:
    """Test cases for format_node_label."""

    def test_title_only(self):
        """Test formatting with title only."""
        label, needs_quotes = format_node_label("Node Title")
        assert label == "Node Title"
        assert needs_quotes is False

    def test_title_with_description(self):
        """Test formatting with title and description."""
        label, needs_quotes = format_node_label("Node Title", "Description text")
        assert label == "Node Title<br/>Description text"
        assert needs_quotes is False

    def test_description_truncation(self):
        """Test that long descriptions are truncated."""
        long_desc = "A" * 150
        label, needs_quotes = format_node_label("Title", long_desc, max_length=100)
        assert "<br/>" in label
        assert len(label.split("<br/>")[1]) <= 100
        assert label.endswith("...")

    def test_special_chars_in_title(self):
        """Test that special characters in title are escaped."""
        label, needs_quotes = format_node_label("A & B", "Description")
        assert "&amp;" in label

    def test_special_chars_in_description(self):
        """Test that special characters in description are escaped."""
        label, needs_quotes = format_node_label("Title", "A < B")
        assert "&lt;" in label

    def test_none_description(self):
        """Test that None description is handled."""
        label, needs_quotes = format_node_label("Title", None)
        assert label == "Title"
        assert needs_quotes is False

    def test_empty_description(self):
        """Test that empty description is handled."""
        label, needs_quotes = format_node_label("Title", "")
        assert label == "Title"
        assert needs_quotes is False

    def test_very_long_title(self):
        """Test that very long titles are preserved."""
        long_title = "A" * 200
        label, needs_quotes = format_node_label(long_title, "Description")
        assert long_title in label

    def test_parentheses_need_quotes(self):
        """Test that labels with parentheses need quotes."""
        label, needs_quotes = format_node_label("Node (Title)")
        assert needs_quotes is True

    def test_brackets_need_quotes(self):
        """Test that labels with brackets need quotes."""
        label, needs_quotes = format_node_label("Node [Title]")
        assert needs_quotes is True
