"""
Mermaid S3 upload node.

This node uploads the Mermaid diagram to S3 for later retrieval.
Single responsibility: S3 upload only.
"""

from src.core.agentic_system.diagrams.nodes.utils.s3_storage import upload_mermaid_to_s3
from logging import getLogger
from uuid import uuid4, UUID

logger = getLogger(__name__)


def mermaid_s3_upload_node(state) -> dict:
    """
    Upload Mermaid diagram to S3.

    Single responsibility: Upload diagram to S3 and generate diagram_id.
    Database persistence is handled by a separate node.

    Args:
        state: GraphState containing mermaid_diagram, user_id, diagram_id (optional)

    Returns:
        Updated state with mermaid_s3_key and diagram_id
    """
    try:
        # Handle both dict and GraphState object access
        mermaid_diagram = (
            state.get("mermaid_diagram")
            if isinstance(state, dict)
            else state.mermaid_diagram
        )
        user_id_str = (
            state.get("user_id") if isinstance(state, dict) else state.user_id
        )
        diagram_id_str = (
            state.get("diagram_id") if isinstance(state, dict) else state.diagram_id
        )

        # Validate required fields
        if mermaid_diagram is None:
            logger.warning("No mermaid_diagram found in state")
            return {"error_message": "No Mermaid diagram found for S3 upload"}

        if user_id_str is None:
            logger.warning("No user_id found in state")
            return {"error_message": "No user_id found for S3 upload"}

        # Convert user_id to UUID
        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid user_id format: {user_id_str}")
            return {"error_message": f"Invalid user_id format: {e}"}

        # Generate diagram_id if not provided
        if diagram_id_str:
            try:
                diagram_id = UUID(diagram_id_str)
            except (ValueError, TypeError):
                logger.warning(f"Invalid diagram_id format: {diagram_id_str}, generating new one")
                diagram_id = uuid4()
        else:
            diagram_id = uuid4()
            logger.info(f"Generated new diagram_id: {diagram_id}")

        # Upload Mermaid diagram to S3 with new path structure
        mermaid_s3_key = upload_mermaid_to_s3(
            mermaid_diagram=mermaid_diagram,
            user_id=user_id,
            diagram_id=diagram_id
        )

        if not mermaid_s3_key:
            logger.warning("S3 upload failed but continuing pipeline")
            return {
                "mermaid_s3_key": None,
                "diagram_id": str(diagram_id),
                "error_message": None,  # Don't fail pipeline if S3 upload fails
            }

        logger.info(f"Mermaid diagram uploaded to S3: {mermaid_s3_key}")

        # Return updated state with both S3 key and diagram_id
        return {
            "mermaid_s3_key": mermaid_s3_key,
            "diagram_id": str(diagram_id),
            "error_message": None,
        }

    except Exception as e:
        logger.error(f"Error in Mermaid S3 upload node: {e}")
        # Don't fail pipeline if S3 upload fails
        return {
            "mermaid_s3_key": None,
            "diagram_id": None,
            "error_message": None,
        }

