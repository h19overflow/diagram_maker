"""
Utility functions for diagram generation nodes.

This package contains utility modules separated by responsibility:
- s3_storage: S3 upload/download and metadata extraction utilities
- database_persistence: Database persistence utilities
- node_utils: Node operation utilities (retrieval, validation, population)
"""

from .s3_storage import (
    upload_mermaid_to_s3,
    get_mermaid_from_s3,
    extract_title_from_user_input,
    extract_description_from_mermaid,
)

from .database_persistence import save_diagram_to_database

from .node_utils import (
    get_retriever,
    populate_node_description,
    search_for_node,
    validate_query_relevance,
)

__all__ = [
    # S3 utilities
    "upload_mermaid_to_s3",
    "get_mermaid_from_s3",
    "extract_title_from_user_input",
    "extract_description_from_mermaid",
    # Database utilities
    "save_diagram_to_database",
    # Node utilities
    "get_retriever",
    "populate_node_description",
    "search_for_node",
    "validate_query_relevance",
]
