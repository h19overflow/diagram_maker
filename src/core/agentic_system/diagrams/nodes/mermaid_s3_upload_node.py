"""
Mermaid S3 upload node.

This node uploads the Mermaid diagram to S3 for later retrieval
and persists diagram metadata to the database.
"""

from src.core.agentic_system.diagrams.nodes.s3_storage import (
    upload_mermaid_to_s3,
    save_diagram_to_database,
    extract_title_from_user_input,
    extract_description_from_mermaid
)
from logging import getLogger
from uuid import uuid4, UUID

logger = getLogger(__name__)


def mermaid_s3_upload_node(state) -> dict:
    """
    Upload Mermaid diagram to S3 and persist metadata to database.

    Args:
        state: GraphState containing mermaid_diagram, user_input, user_id, diagram_id

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
        user_input = (
            state.get("user_input") if isinstance(state, dict) else state.user_input
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

        # Extract title and description for database
        title = extract_title_from_user_input(user_input)
        description = extract_description_from_mermaid(mermaid_diagram)

        # Save diagram metadata to database
        db_save_success = save_diagram_to_database(
            user_id=user_id,
            diagram_id=diagram_id,
            s3_path=mermaid_s3_key,
            title=title,
            user_query=user_input if user_input else "",
            mermaid_code=mermaid_diagram,
            description=description,
            status="draft"
        )

        if not db_save_success:
            logger.warning(
                f"Database save failed for diagram {diagram_id}, but S3 upload succeeded. "
                "Continuing with pipeline."
            )

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

