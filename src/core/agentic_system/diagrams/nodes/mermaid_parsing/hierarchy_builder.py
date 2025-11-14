"""
Hierarchy building utilities for organizing nodes by level.

This module provides functions to group nodes by hierarchy level
and build parent-child relationships for efficient diagram generation.
"""

from typing import Dict, List, Tuple, Optional
from src.core.agentic_system.respone_formats import Nodes, Edges


def group_nodes_by_level(nodes: Nodes) -> Dict[int, List[Tuple[str, str, Optional[str]]]]:
    """
    Group nodes by hierarchy level.
    
    Extracts nodes from the Nodes object and groups them by hierarchy_level.
    Each node is represented as a tuple of (node_id, title, description).
    
    Args:
        nodes: Nodes object containing lists of node data
        
    Returns:
        Dictionary mapping hierarchy level to list of node tuples
        Format: {level: [(node_id, title, description), ...]}
        
    Example:
        >>> nodes = Nodes(
        ...     id=["n1", "n2"],
        ...     title=["Title1", "Title2"],
        ...     hierarchy_level=[0, 1],
        ...     parent_node_id=[None, "n1"],
        ...     description=["Desc1", "Desc2"]
        ... )
        >>> group_nodes_by_level(nodes)
        {0: [('n1', 'Title1', 'Desc1')], 1: [('n2', 'Title2', 'Desc2')]}
    """
    grouped: Dict[int, List[Tuple[str, str, Optional[str]]]] = {}
    
    # Extract node data from the Nodes object
    node_ids = nodes.id
    titles = nodes.title
    hierarchy_levels = nodes.hierarchy_level
    descriptions = nodes.description if nodes.description else [None] * len(node_ids)
    
    # Validate all lists have the same length
    if not all(len(lst) == len(node_ids) for lst in [titles, hierarchy_levels]):
        raise ValueError(f"Mismatched list lengths in Nodes object: ids={len(node_ids)}, titles={len(titles)}, levels={len(hierarchy_levels)}")
    
    # Group nodes by hierarchy level
    for i, node_id in enumerate(node_ids):
        level = hierarchy_levels[i]
        title = titles[i]
        description = descriptions[i] if i < len(descriptions) else None
        
        if level not in grouped:
            grouped[level] = []
        
        grouped[level].append((node_id, title, description))
    
    return grouped


def build_hierarchy_tree(nodes: Nodes, edges: Edges) -> Dict[str, List[str]]:
    """
    Build parent-child relationships from nodes and edges.
    
    Creates a dictionary mapping parent node IDs to their child node IDs
    for efficient traversal during diagram generation.
    
    Args:
        nodes: Nodes object containing node data
        edges: Edges object containing edge relationships
        
    Returns:
        Dictionary mapping parent ID to list of child IDs
        Format: {parent_id: [child_id, ...]}
        
    Example:
        >>> nodes = Nodes(id=["n1", "n2"], ...)
        >>> edges = Edges(source=["n1"], target=["n2"])
        >>> build_hierarchy_tree(nodes, edges)
        {'n1': ['n2']}
    """
    tree: Dict[str, List[str]] = {}
    
    # Build tree from edges
    sources = edges.source
    targets = edges.target
    
    for i, source in enumerate(sources):
        target = targets[i]
        
        if source not in tree:
            tree[source] = []
        
        tree[source].append(target)
    
    # Also build from parent_node_id relationships in nodes
    node_ids = nodes.id
    parent_node_ids = nodes.parent_node_id
    
    for i, node_id in enumerate(node_ids):
        parent_id = parent_node_ids[i]
        if parent_id is not None:
            if parent_id not in tree:
                tree[parent_id] = []
            if node_id not in tree[parent_id]:
                tree[parent_id].append(node_id)
    
    return tree

