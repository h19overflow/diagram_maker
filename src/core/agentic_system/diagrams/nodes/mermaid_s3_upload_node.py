"""
Mermaid S3 upload node.

This node uploads the Mermaid diagram to S3 for later retrieval.
"""

from src.core.agentic_system.diagrams.nodes.s3_storage import upload_mermaid_to_s3
from logging import getLogger

logger = getLogger(__name__)


def mermaid_s3_upload_node(state) -> dict:
    """
    Upload Mermaid diagram to S3.

    Args:
        state: GraphState containing mermaid_diagram, user_input

    Returns:
        Updated state with mermaid_s3_key
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
            return {"error_message": "No Mermaid diagram found for S3 upload"}

        # Use user_input as diagram title
        diagram_title = user_input if user_input else "Diagram"

        # Upload Mermaid diagram to S3
        mermaid_s3_key = upload_mermaid_to_s3(
            mermaid_diagram, diagram_title=diagram_title, user_input=user_input
        )

        if mermaid_s3_key:
            logger.info(f"Mermaid diagram uploaded to S3: {mermaid_s3_key}")
            return {
                "mermaid_s3_key": mermaid_s3_key,
                "error_message": None,
            }
        else:
            logger.warning("S3 upload failed but continuing pipeline")
            return {
                "mermaid_s3_key": None,
                "error_message": None,  # Don't fail pipeline if S3 upload fails
            }
    except Exception as e:
        logger.error(f"Error in Mermaid S3 upload node: {e}")
        # Don't fail pipeline if S3 upload fails
        return {
            "mermaid_s3_key": None,
            "error_message": None,
        }

