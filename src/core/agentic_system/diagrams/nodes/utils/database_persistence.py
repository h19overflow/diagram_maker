"""
Database persistence utilities for diagram metadata.

This module handles saving diagram metadata to the PostgreSQL database.
Separated from S3 storage to maintain single responsibility.
"""

from src.boundary.database import get_session
from src.boundary.repositories.diagram_repository import DiagramRepository
from logging import getLogger
from uuid import UUID

logger = getLogger(__name__)


def save_diagram_to_database(
    user_id: UUID,
    diagram_id: UUID,
    s3_path: str,
    title: str,
    user_query: str,
    mermaid_code: str,
    description: str = None,
    status: str = "draft"
) -> bool:
    """
    Save diagram metadata to database.

    Args:
        user_id: User UUID (foreign key)
        diagram_id: Diagram UUID (primary key)
        s3_path: Full S3 path to the .mmd file
        title: Diagram title
        user_query: Original user query
        mermaid_code: Generated Mermaid code
        description: Optional description
        status: Diagram status (default: "draft")

    Returns:
        True if save successful, False otherwise
    """
    try:
        with get_session() as session:
            diagram_repo = DiagramRepository(session)
            diagram = diagram_repo.create_diagram(
                user_id=user_id,
                diagram_id=diagram_id,
                s3_path=s3_path,
                title=title,
                user_query=user_query,
                mermaid_code=mermaid_code,
                description=description,
                status=status
            )
            logger.info(f"Diagram {diagram.diagram_id} saved to database for user {user_id}")
            return True
    except Exception as db_error:
        logger.error(f"Failed to save diagram to database: {db_error}")
        return False
