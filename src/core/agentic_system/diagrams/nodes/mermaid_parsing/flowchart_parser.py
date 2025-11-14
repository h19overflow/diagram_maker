"""
Flowchart parser for converting IRSDiagramResponse to Mermaid flowchart syntax.

This module provides the main function to convert structured diagram data
into Mermaid flowchart syntax with hierarchy visualization using different
node shapes based on hierarchy level.
"""

from src.core.agentic_system.respone_formats import IRSDiagramResponse
from .node_formatter import sanitize_node_id, format_node_label
from .hierarchy_builder import group_nodes_by_level
from logging import getLogger
from pathlib import Path
from datetime import datetime

logger = getLogger(__name__)


def _get_node_shape(level: int) -> tuple[str, str]:
    """
    Get Mermaid node shape syntax based on hierarchy level.

    Different shapes are used for different hierarchy levels:
    - Level 0 (root): Rectangles [text]
    - Level 1: Rounded rectangles (text)
    - Level 2: Stadium shapes ([text])
    - Level 3+: Cylinders [(text)]

    Args:
        level: Hierarchy level (0 = root, increases for deeper nodes)

    Returns:
        Tuple of (opening_bracket, closing_bracket) for Mermaid syntax
    """
    if level == 0:
        return ("[", "]")  # Rectangle
    elif level == 1:
        return ("[", "]")  # Rounded rectangle
    elif level == 2:
        return ("[", "]")  # Stadium shape
    else:
        return ("[", "]")  # Cylinder shape


def parse_to_flowchart(diagram: IRSDiagramResponse) -> str:
    """
    Convert IRSDiagramResponse to Mermaid flowchart syntax.

    Generates a Mermaid flowchart with:
    - Different node shapes based on hierarchy level
    - Node labels containing title and description (in the box)
    - Edges connecting nodes based on relationships

    Args:
        diagram: IRSDiagramResponse object containing nodes and edges

    Returns:
        Mermaid flowchart syntax as a string

    Raises:
        ValueError: If diagram structure is invalid

    Example:
        >>> diagram = IRSDiagramResponse(
        ...     diagram_type=DiagramType.flowchart,
        ...     title="Test Diagram",
        ...     nodes=[Nodes(id=["n1"], title=["Node1"], ...)],
        ...     edges=[Edges(source=[], target=[])]
        ... )
        >>> mermaid = parse_to_flowchart(diagram)
        >>> "flowchart TD" in mermaid
        True
    """
    # Validate diagram structure
    if not diagram.nodes or len(diagram.nodes) == 0:
        logger.warning("No nodes found in diagram")
        return "flowchart TD\n    Empty[No nodes]"

    if not diagram.edges or len(diagram.edges) == 0:
        logger.warning("No edges found in diagram")

    # Extract first Nodes and Edges objects (diagram contains lists)
    nodes_obj = diagram.nodes[0]
    edges_obj = diagram.edges[0] if diagram.edges and len(diagram.edges) > 0 else None

    # Validate nodes have data
    if not nodes_obj.id or len(nodes_obj.id) == 0:
        logger.warning("Nodes object has no node IDs")
        return "flowchart TD\n    Empty[No nodes]"

    # Group nodes by hierarchy level
    grouped_nodes = group_nodes_by_level(nodes_obj)

    # Create mapping of original node IDs to sanitized IDs
    # Handle potential duplicates by appending index if needed
    node_id_map: dict[str, str] = {}
    sanitized_to_count: dict[str, int] = {}
    for node_id in nodes_obj.id:
        sanitized = sanitize_node_id(node_id)
        # If we've seen this sanitized ID before, append a counter
        if sanitized in sanitized_to_count:
            sanitized_to_count[sanitized] += 1
            sanitized = f"{sanitized}_{sanitized_to_count[sanitized]}"
        else:
            sanitized_to_count[sanitized] = 0
        node_id_map[node_id] = sanitized

    # Build Mermaid flowchart
    lines = ["flowchart TD"]

    # Define all nodes with appropriate shapes and labels
    for level in sorted(grouped_nodes.keys()):
        for node_id, title, description in grouped_nodes[level]:
            sanitized_id = node_id_map[node_id]
            label, needs_quotes_flag = format_node_label(title, description)
            shape_open, shape_close = _get_node_shape(level)

            # Wrap label in quotes if it contains special characters
            if needs_quotes_flag:
                formatted_label = f'"{label}"'
            else:
                formatted_label = label

            # Format: NodeID[Label] or NodeID(Label) etc.
            node_line = f"    {sanitized_id}{shape_open}{formatted_label}{shape_close}"
            lines.append(node_line)

    # Add edges
    if edges_obj and edges_obj.source and len(edges_obj.source) > 0:
        # Validate that source and target lists have the same length
        if not edges_obj.target or len(edges_obj.target) != len(edges_obj.source):
            logger.warning(
                f"Edge source and target lists have mismatched lengths: {len(edges_obj.source)} sources vs {len(edges_obj.target) if edges_obj.target else 0} targets"
            )
        else:
            for i, source_id in enumerate(edges_obj.source):
                target_id = edges_obj.target[i]

                # Get sanitized IDs
                sanitized_source = node_id_map.get(source_id)
                sanitized_target = node_id_map.get(target_id)

                # Skip if either node is missing from the map
                if not sanitized_source or not sanitized_target:
                    logger.warning(
                        f"Skipping edge: {source_id} -> {target_id} (node not found)"
                    )
                    continue

                # Add edge: Source --> Target
                edge_line = f"    {sanitized_source} --> {sanitized_target}"
                lines.append(edge_line)

    # Join all lines
    mermaid_code = "\n".join(lines)

    logger.info(f"Generated Mermaid flowchart with {len(nodes_obj.id)} nodes")

    return mermaid_code


def save_mermaid_to_file(
    mermaid_code: str, diagram_title: str = None, output_dir: str = "Docs"
) -> str:
    r"""
    Save Mermaid code to a .mmd file.

    The file will be saved in the specified output directory with a filename
    based on the diagram title (sanitized) or a timestamp if no title is provided.

    Args:
        mermaid_code: The Mermaid diagram syntax to save
        diagram_title: Optional title for the diagram (used for filename)
        output_dir: Directory to save the file (default: "Docs")

    Returns:
        Path to the saved file as a string

    Raises:
        IOError: If the file cannot be written

    Example:
        >>> mermaid = "flowchart TD\n    A[Node A]"
        >>> filepath = save_mermaid_to_file(mermaid, "My Diagram")
        >>> filepath.endswith(".mmd")
        True
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate filename from title or use timestamp
    if diagram_title:
        # Sanitize title for filename
        safe_title = "".join(
            c for c in diagram_title if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        safe_title = safe_title.replace(" ", "_")
        if not safe_title:
            safe_title = "diagram"
        filename = f"{safe_title}.mmd"
    else:
        # Use timestamp if no title
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diagram_{timestamp}.mmd"

    # Full file path
    filepath = output_path / filename

    # Write the mermaid code to file
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(mermaid_code)
        logger.info(f"Saved Mermaid diagram to {filepath}")
        return str(filepath)
    except IOError as e:
        logger.error(f"Failed to save Mermaid diagram to {filepath}: {e}")
        raise
