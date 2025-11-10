from pydantic import BaseModel, Field
from typing import Optional, Any
from .graphs import GenerateVariantRequest


class GenerateDraftRequest(BaseModel):
    doc_key: str = Field(..., description="s3-kb key under uploads/ or corpus/")
    variant_request: Optional[GenerateVariantRequest] = None  # optional
    views: Optional[list[str]] = None  # e.g. ["flowchart","concept"]


class GenerateDraftResponse(BaseModel):
    draft_id: str
    mermaid: str
    summary: Optional[str] = None
    graph_json: Optional[Any] = None


class SaveDraftRequest(BaseModel):
    draft_id: Optional[str] = None
    draft_name: str
    draft_tags: list[str] = []


class SaveDraftResponse(BaseModel):
    draft_id: str

