"""
S3 storage utilities for diagram persistence.

This module handles uploading and retrieving Mermaid diagrams from S3
for later retrieval and sharing. Also handles database persistence of diagram metadata.
"""

from src.boundary.s3_client import generate_presigned_url, request_via_presigned_url
from src.boundary.database import get_session
from src.boundary.repositories.diagram_repository import DiagramRepository
from logging import getLogger
from datetime import datetime
from uuid import UUID
import hashlib
import re

logger = getLogger(__name__)


def extract_title_from_user_input(user_input: str) -> str:
    """
    Extract a title from user input.

    Takes the first sentence or first 100 characters, whichever is shorter.
    Cleans up the text to be suitable for a title.

    Args:
        user_input: The user's query/input

    Returns:
        Extracted title (max 255 chars to match DB constraint)
    """
    if not user_input:
        return "Untitled Diagram"

    # Take first sentence (up to first period, question mark, or exclamation)
    first_sentence_match = re.match(r'^([^.!?]+)[.!?]?', user_input.strip())
    if first_sentence_match:
        title = first_sentence_match.group(1).strip()
    else:
        title = user_input.strip()

    # Limit to 100 chars for readability
    if len(title) > 100:
        title = title[:97] + "..."

    # Ensure it doesn't exceed database constraint
    return title[:255] if title else "Untitled Diagram"


def extract_description_from_mermaid(mermaid_code: str) -> str:
    """
    Extract a description from the Mermaid diagram code.

    Analyzes the diagram structure to generate a meaningful description.
    Counts nodes, edges, and identifies diagram type.

    Args:
        mermaid_code: The Mermaid diagram syntax

    Returns:
        Generated description
    """
    if not mermaid_code:
        return None

    try:
        lines = mermaid_code.strip().split('\n')

        # Identify diagram type from first line
        diagram_type = "diagram"
        if lines:
            first_line = lines[0].strip().lower()
            if 'flowchart' in first_line or 'graph' in first_line:
                diagram_type = "flowchart"
            elif 'sequencediagram' in first_line:
                diagram_type = "sequence diagram"
            elif 'classDiagram' in first_line:
                diagram_type = "class diagram"
            elif 'erdiagram' in first_line:
                diagram_type = "entity-relationship diagram"
            elif 'gantt' in first_line:
                diagram_type = "gantt chart"
            elif 'pie' in first_line:
                diagram_type = "pie chart"

        # Count nodes and relationships
        node_count = 0
        edge_count = 0

        for line in lines[1:]:  # Skip first line (diagram type declaration)
            line = line.strip()
            if not line or line.startswith('%%'):  # Skip empty lines and comments
                continue

            # Count edges (arrows like -->, --->, ==>)
            if '-->' in line or '--->' in line or '==>' in line or '--' in line:
                edge_count += 1
            # Count nodes (lines with [ ] or ( ) or { })
            elif '[' in line or '(' in line or '{' in line:
                node_count += 1

        # Generate description
        description_parts = [f"A {diagram_type}"]
        if node_count > 0:
            description_parts.append(f"with {node_count} nodes")
        if edge_count > 0:
            description_parts.append(f"and {edge_count} connections")

        return " ".join(description_parts) + "."

    except Exception as e:
        logger.warning(f"Failed to extract description from mermaid code: {e}")
        return "Generated diagram"


def upload_mermaid_to_s3(
    mermaid_diagram: str,
    user_id: UUID,
    diagram_id: UUID
) -> str | None:
    """
    Upload a Mermaid diagram to S3 using user-specific path structure.

    New path structure: users/{user_id}/diagrams/{diagram_id}.mmd

    Args:
        mermaid_diagram: The Mermaid diagram syntax string
        user_id: User UUID for organizing S3 path
        diagram_id: Diagram UUID for unique file naming

    Returns:
        S3 key (path) if upload successful, None if upload failed
    """
    try:
        # New S3 path structure: users/{user_id}/diagrams/{diagram_id}.mmd
        s3_key = f"users/{user_id}/diagrams/{diagram_id}.mmd"

        # Generate presigned URL and upload
        presigned_url = generate_presigned_url(
            s3_key, "put_object", expires_in=3600, content_type="text/plain"
        )
        request_via_presigned_url(
            presigned_url, "PUT", mermaid_diagram, content_type="text/plain"
        )
        logger.info(f"Mermaid diagram uploaded to S3: {s3_key}")
        return s3_key
    except Exception as s3_error:
        logger.warning(f"Failed to upload Mermaid diagram to S3: {s3_error}")
        return None


def get_mermaid_from_s3(s3_key: str) -> str | None:
    """
    Retrieve a Mermaid diagram from S3 using its key.

    Args:
        s3_key: The S3 key of the diagram to retrieve

    Returns:
        Mermaid diagram string if retrieval successful, None if failed
    """
    try:
        presigned_url = generate_presigned_url(s3_key, "get_object", expires_in=3600)
        mermaid_diagram = request_via_presigned_url(presigned_url, "GET")
        logger.info(f"Mermaid diagram retrieved from S3: {s3_key}")
        return mermaid_diagram
    except Exception as s3_error:
        logger.warning(f"Failed to retrieve Mermaid diagram from S3: {s3_error}")
        return None


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
