"""
FastAPI router for diagram generation endpoints.

This module provides endpoints for generating diagrams using the LangGraph-based
diagram generation system. It orchestrates the flow from user input to final Mermaid diagram.
"""

from fastapi import APIRouter, HTTPException
from logging import getLogger
from uuid import UUID

from src.api.schemas.graphs import GenerateDiagramRequest, GenerateDiagramResponse
from src.api.schemas.drafts import SaveDraftRequest, SaveDraftResponse
from src.core.agentic_system.diagrams.graph import diagram_graph
from src.core.agentic_system.diagrams.graph_state import GraphState
from src.boundary.database import get_session
from src.boundary.repositories.user_repository import UserRepository

logger = getLogger(__name__)

router = APIRouter(prefix="/api/v1/diagrams", tags=["diagrams"])


@router.post("/generate", response_model=GenerateDiagramResponse)
async def generate_diagram(request: GenerateDiagramRequest):
    """
    Generate a Mermaid diagram from user input.

    Args:
        request: GenerateDiagramRequest containing user_input query and user_id

    Returns:
        GenerateDiagramResponse with mermaid_diagram, filepath, diagram_id, and optional error

    Raises:
        HTTPException: If diagram generation fails critically or user_id is invalid
    """
    logger.info(f"Received diagram generation request: {request.user_input[:100]}...")

    # Validate user_id format
    try:
        user_uuid = UUID(request.user_id)
    except ValueError:
        logger.error(f"Invalid user_id format: {request.user_id}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid user_id format. Must be a valid UUID. Received: {request.user_id}"
        )

    # Persist or retrieve user from database
    try:
        with get_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_or_create_user(user_uuid)
            logger.info(f"User {user.user_id} ready for diagram generation")
    except Exception as db_error:
        logger.error(f"Failed to persist user {user_uuid}: {db_error}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to persist user: {str(db_error)}"
        )

    try:
        # Create initial state with user input and user_id
        initial_state = GraphState(
            user_input=request.user_input,
            user_id=str(user_uuid)
        )

        # Run the diagram generation graph
        final_state = diagram_graph.invoke(initial_state)

        # Extract results from final state (dictionary)
        error_message = final_state.get("error_message")
        mermaid_diagram = final_state.get("mermaid_diagram")
        mermaid_filepath = final_state.get("mermaid_filepath")
        diagram_id = final_state.get("diagram_id")

        # If there's an error but no diagram, return error response
        if error_message and not mermaid_diagram:
            logger.error(f"Diagram generation failed: {error_message}")
            return GenerateDiagramResponse(
                mermaid_diagram="",
                error_message=error_message
            )

        # If no diagram was generated and no error, something went wrong
        if not mermaid_diagram:
            logger.error("No diagram generated and no error message")
            raise HTTPException(
                status_code=500,
                detail="Diagram generation failed without specific error message"
            )

        logger.info("Diagram generation completed successfully")
        return GenerateDiagramResponse(
            mermaid_diagram=mermaid_diagram,
            mermaid_filepath=mermaid_filepath,
            diagram_id=diagram_id,
            error_message=error_message  # May contain warnings even if diagram exists
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Exception during diagram generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Diagram generation failed: {str(e)}"
        )


@router.post("/save-draft", response_model=SaveDraftResponse)
async def save_draft(request: SaveDraftRequest):
    """Save a draft diagram."""
    return SaveDraftResponse(draft_id=request.draft_id or "draft_new")
