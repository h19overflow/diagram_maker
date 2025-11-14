from fastapi import APIRouter
from src.api.schemas.chat import ChatRequest, ChatResponse
from src.api.schemas.drafts import GenerateDraftRequest, GenerateDraftResponse
from src.core.agentic_system.artist_mode import invoke_artist_mode, invoke_chat_only
import logging

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
logger = logging.getLogger(__name__)


@router.post("/request", response_model=ChatResponse)
async def chat_request(request: ChatRequest):
    """
    Handle chat requests with optional artist mode.

    Args:
        request: ChatRequest with message and artist_mode flag

    Returns:
        ChatResponse with text reply and optional diagram

    Artist Mode:
    - When artist_mode=False: Returns text answer only
    - When artist_mode=True: Returns text answer + visual diagram (parallel execution)
    """
    logger.info(
        f"Received chat request (artist_mode={request.artist_mode}): {request.message[:50]}..."
    )

    try:
        if request.artist_mode:
            # Artist mode: invoke both chat and diagram in parallel
            logger.info("Processing in artist mode (chat + diagram)")
            response = await invoke_artist_mode(request.message)
        else:
            # Regular mode: invoke chat only
            logger.info("Processing in chat-only mode")
            response = await invoke_chat_only(request.message)

        logger.info("Request processed successfully")
        return response

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        # Return error response
        return ChatResponse(
            reply=f"An error occurred while processing your request: {str(e)}",
            sources=None,
            score=0.0,
        )


@router.post("/generate-draft", response_model=GenerateDraftResponse)
async def generate_draft(request: GenerateDraftRequest):
    return GenerateDraftResponse(
        draft_id="draft_123",
        mermaid="graph TD\n    A[Start] --> B[End]",
        summary="Sample draft",
    )
