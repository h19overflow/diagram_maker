from fastapi import APIRouter, File, UploadFile
from src.api.schemas.uploads import PresignRequest, PresignResponse

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])


@router.post("/presign", response_model=PresignResponse)
async def presign(request: PresignRequest, file_upload: UploadFile = File(...)):
    return PresignResponse(
        url=request.url, key=request.key, mime=file_upload.content_type
    )
