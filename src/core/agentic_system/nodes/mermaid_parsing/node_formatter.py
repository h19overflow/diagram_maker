"""
Node formatting utilities for Mermaid compatibility.

This module provides functions to sanitize node IDs and format labels
for Mermaid diagram syntax.
"""

import re
from typing import Optional


def sanitize_node_id(node_id: str) -> str:
    """
    Convert node IDs to Mermaid-safe format.
    
    Mermaid node IDs must be alphanumeric with underscores and hyphens.
    Special characters are replaced with underscores.
    
    Args:
        node_id: Original node ID string
        
    Returns:
        Sanitized node ID safe for Mermaid syntax
        
    Example:
        >>> sanitize_node_id("node-1")
        'node-1'
        >>> sanitize_node_id("node.1.2")
        'node_1_2'
        >>> sanitize_node_id("Node (1)")
        'Node__1_'
    """
    # Replace special characters (except alphanumeric, underscore, hyphen) with underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', node_id)
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'node'
    return sanitized


def escape_mermaid_text(text: str) -> str:
    """
    Escape special Mermaid characters in text.
    
    Mermaid has special characters that need escaping in labels:
    - Quotes, parentheses, brackets, etc. may need escaping
    - HTML entities are supported in labels
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for Mermaid labels
    """
    if not text:
        return ""
    
    # Replace HTML-unsafe characters with HTML entities
    # Mermaid supports HTML entities in labels
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    # Escape quotes that might break syntax
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    
    return text


def format_node_label(title: str, description: Optional[str] = None, max_length: int = 100) -> str:
    """
    Format node labels with description included in the box.
    
    Combines title and description with <br/> separator.
    Truncates description if too long (preserves title).
    
    Args:
        title: Node title (always included)
        description: Optional node description
        max_length: Maximum length for description (title is preserved)
        
    Returns:
        Formatted label string with title and optional description
        
    Example:
        >>> format_node_label("Node Title", "Description text")
        'Node Title<br/>Description text'
        >>> format_node_label("Node Title", None)
        'Node Title'
    """
    # Escape both title and description
    escaped_title = escape_mermaid_text(title)
    
    if not description:
        return escaped_title
    
    # Escape and truncate description if needed
    escaped_description = escape_mermaid_text(description)
    
    # Truncate description if it exceeds max_length
    if len(escaped_description) > max_length:
        escaped_description = escaped_description[:max_length - 3] + "..."
    
    # Combine with <br/> separator for line break in Mermaid
    return f"{escaped_title}<br/>{escaped_description}"

