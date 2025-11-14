"""
Database persistence node.

This node persists diagram metadata to the database after S3 upload.
Separated from S3 upload to maintain single responsibility principle.
"""

from src.core.agentic_system.diagrams.nodes.utils.database_persistence import save_diagram_to_database
from src.core.agentic_system.diagrams.nodes.utils.s3_storage import (
    extract_title_from_user_input,
    extract_description_from_mermaid
)
from logging import getLogger
from uuid import UUID

logger = getLogger(__name__)


def database_persistence_node(state) -> dict:
    """
    Persist diagram metadata to database.

    Args:
        state: GraphState containing user_id, diagram_id, mermaid_diagram,
               user_input, mermaid_s3_key

    Returns:
        Updated state (empty dict, no modifications needed)
    """
    try:
        # Handle both dict and GraphState object access
        user_id_str = (
            state.get("user_id") if isinstance(state, dict) else state.user_id
        )
        diagram_id_str = (
            state.get("diagram_id") if isinstance(state, dict) else state.diagram_id
        )
        mermaid_diagram = (
            state.get("mermaid_diagram")
            if isinstance(state, dict)
            else state.mermaid_diagram
        )
        user_input = (
            state.get("user_input") if isinstance(state, dict) else state.user_input
        )
        mermaid_s3_key = (
            state.get("mermaid_s3_key")
            if isinstance(state, dict)
            else state.mermaid_s3_key
        )

        # Validate required fields
        if not user_id_str:
            logger.warning("No user_id found in state, skipping database save")
            return {}

        if not diagram_id_str:
            logger.warning("No diagram_id found in state, skipping database save")
            return {}

        if not mermaid_s3_key:
            logger.warning("No S3 key found in state, skipping database save")
            return {}

        if not mermaid_diagram:
            logger.warning("No mermaid_diagram found in state, skipping database save")
            return {}

        # Convert IDs to UUID
        try:
            user_id = UUID(user_id_str)
            diagram_id = UUID(diagram_id_str)
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid UUID format: {e}")
            return {}

        # Extract title and description
        title = extract_title_from_user_input(user_input)
        description = extract_description_from_mermaid(mermaid_diagram)

        # Save to database
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

        if db_save_success:
            logger.info(f"Successfully saved diagram {diagram_id} to database")
        else:
            logger.warning(f"Failed to save diagram {diagram_id} to database")

        # Return empty dict - no state modifications needed
        return {}

    except Exception as e:
        logger.error(f"Error in database persistence node: {e}")
        # Don't fail pipeline if database save fails
        return {}
