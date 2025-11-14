"""
Mermaid generation node.

This node generates Mermaid diagram syntax from the final diagram structure.
"""

from src.core.agentic_system.diagrams.nodes.mermaid_parsing import parse_to_flowchart
from logging import getLogger

logger = getLogger(__name__)


def mermaid_generation_node(state) -> dict:
    """
    Generate Mermaid diagram syntax from the final diagram.

    Args:
        state: GraphState containing final_diagram

    Returns:
        Updated state with mermaid_diagram
    """
    try:
        # Handle both dict and GraphState object access
        final_diagram = (
            state.get("final_diagram")
            if isinstance(state, dict)
            else state.final_diagram
        )

        if final_diagram is None:
            logger.warning("No final_diagram found in state")
            return {"error_message": "No final diagram found for Mermaid generation"}

        # Generate Mermaid diagram syntax
        try:
            mermaid_diagram = parse_to_flowchart(final_diagram)
            logger.info("Successfully generated Mermaid diagram syntax")
            return {
                "mermaid_diagram": mermaid_diagram,
                "error_message": None,
            }
        except Exception as e:
            logger.warning(f"Failed to generate Mermaid diagram: {e}")
            return {
                "mermaid_diagram": None,
                "error_message": f"Failed to generate Mermaid diagram: {e}",
            }
    except Exception as e:
        logger.error(f"Error in Mermaid generation node: {e}")
        return {"error_message": f"Error in Mermaid generation node: {e}"}

