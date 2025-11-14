"""
FastAPI router for diagram generation endpoints.

This module provides endpoints for generating diagrams using the LangGraph-based
diagram generation system. It orchestrates the flow from user input to final Mermaid diagram.
"""

from fastapi import APIRouter, HTTPException
from logging import getLogger

from src.api.schemas.graphs import GenerateDiagramRequest, GenerateDiagramResponse
from src.api.schemas.drafts import SaveDraftRequest, SaveDraftResponse
from src.core.agentic_system.diagrams.graph import diagram_graph
from src.core.agentic_system.diagrams.graph_state import GraphState

logger = getLogger(__name__)

router = APIRouter(prefix="/api/v1/diagrams", tags=["diagrams"])


@router.post("/generate", response_model=GenerateDiagramResponse)
async def generate_diagram(request: GenerateDiagramRequest):
    """
    Generate a Mermaid diagram from user input.

    Args:
        request: GenerateDiagramRequest containing user_input query

    Returns:
        GenerateDiagramResponse with mermaid_diagram, filepath, and optional error

    Raises:
        HTTPException: If diagram generation fails critically
    """
    logger.info(f"Received diagram generation request: {request.user_input[:100]}...")

    try:
        # Create initial state with user input
        initial_state = GraphState(user_input=request.user_input)

        # Run the diagram generation graph
        final_state = diagram_graph.invoke(initial_state)

        # Extract results from final state (dictionary)
        error_message = final_state.get("error_message")
        mermaid_diagram = final_state.get("mermaid_diagram")
        mermaid_filepath = final_state.get("mermaid_filepath")

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
            error_message=error_message  # May contain warnings even if diagram exists
        )

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
