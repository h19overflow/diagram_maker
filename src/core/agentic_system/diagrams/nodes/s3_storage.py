"""
S3 storage utilities for diagram persistence.

This module handles uploading and retrieving Mermaid diagrams from S3
for later retrieval and sharing.
"""

from src.boundary.s3_client import generate_presigned_url, request_via_presigned_url
from logging import getLogger
from datetime import datetime
import hashlib

logger = getLogger(__name__)


def upload_mermaid_to_s3(
    mermaid_diagram: str, diagram_title: str = None, user_input: str = None
) -> str | None:
    """
    Upload a Mermaid diagram to S3 for later retrieval.

    Args:
        mermaid_diagram: The Mermaid diagram syntax string
        diagram_title: Optional title for the diagram (used in S3 key)
        user_input: Optional user input (used for uniqueness in S3 key)

    Returns:
        S3 key if upload successful, None if upload failed
    """
    try:
        # Generate unique S3 key based on timestamp and diagram title
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = (
            "".join(c for c in diagram_title if c.isalnum() or c in (" ", "-", "_"))
            .strip()
            .replace(" ", "_")
            if diagram_title
            else "diagram"
        )
        if not safe_title:
            safe_title = "diagram"
        # Create hash of user input for uniqueness
        input_hash = hashlib.md5(
            user_input.encode() if user_input else b"", usedforsecurity=False
        ).hexdigest()[:8]
        s3_key = f"diagrams/{timestamp}_{safe_title}_{input_hash}.mmd"

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
