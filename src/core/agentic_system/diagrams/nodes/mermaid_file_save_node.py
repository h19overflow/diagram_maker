"""
Mermaid file save node.

This node saves the Mermaid diagram to a local file.
"""

from src.core.agentic_system.diagrams.nodes.mermaid_parsing import save_mermaid_to_file
from logging import getLogger

logger = getLogger(__name__)


def mermaid_file_save_node(state) -> dict:
    """
    Save Mermaid diagram to a local file.

    Args:
        state: GraphState containing mermaid_diagram and user_input

    Returns:
        Updated state with mermaid_filepath
    """
    try:
        # Handle both dict and GraphState object access
        mermaid_diagram = (
            state.get("mermaid_diagram")
            if isinstance(state, dict)
            else state.mermaid_diagram
        )
        user_input = (
            state.get("user_input") if isinstance(state, dict) else state.user_input
        )

        if mermaid_diagram is None:
            logger.warning("No mermaid_diagram found in state")
            return {"error_message": "No Mermaid diagram found for file save"}

        # Use user_input as diagram title, or default
        diagram_title = user_input if user_input else "Diagram"

        # Save Mermaid diagram to file
        try:
            mermaid_filepath = save_mermaid_to_file(
                mermaid_diagram, diagram_title=diagram_title
            )
            logger.info(f"Mermaid diagram saved to {mermaid_filepath}")
            return {
                "mermaid_filepath": mermaid_filepath,
                "error_message": None,
            }
        except Exception as save_error:
            logger.warning(f"Failed to save Mermaid diagram to file: {save_error}")
            return {
                "mermaid_filepath": None,
                "error_message": f"Failed to save Mermaid diagram: {save_error}",
            }
    except Exception as e:
        logger.error(f"Error in Mermaid file save node: {e}")
        return {"error_message": f"Error in Mermaid file save node: {e}"}

