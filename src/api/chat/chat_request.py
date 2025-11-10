from fastapi import APIRouter
from src.api.schemas.chat import ChatRequest, ChatResponse
from src.api.schemas.drafts import GenerateDraftRequest, GenerateDraftResponse
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])




@router.post("/request", response_model=ChatResponse)
async def chat_request(request: ChatRequest):
    return ChatResponse(
        reply="Hello, world!", sources=["source1", "source2"], score=0.95
    )


@router.post("/generate-draft", response_model=GenerateDraftResponse)
async def generate_draft(request: GenerateDraftRequest):
    return GenerateDraftResponse(
        draft_id="draft_123",
        mermaid="graph TD\n    A[Start] --> B[End]",
        summary="Sample draft",
    )
