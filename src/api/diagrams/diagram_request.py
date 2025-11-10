from src.api.schemas.drafts import SaveDraftRequest, SaveDraftResponse
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/drafts", tags=["drafts"])


@router.post("/save-draft", response_model=SaveDraftResponse)
async def save_draft(request: SaveDraftRequest):
    return SaveDraftResponse(draft_id=request.draft_id or "draft_new")
