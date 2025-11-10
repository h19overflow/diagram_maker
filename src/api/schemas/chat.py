from pydantic import BaseModel, Field, ConfigDict, conlist, confloat
from typing import Optional
from .enums import DiagramType


class ChatRequest(BaseModel):
    message: str
    artist_mode: bool = False
    context_id: Optional[str] = None


class GraphSnippet(BaseModel):
    type: DiagramType
    mermaid: str


class ChatResponse(BaseModel):
    reply: str
    graphs: Optional[conlist(GraphSnippet, max_length=4)] = None
    sources: Optional[list[str]] = None
    score: Optional[confloat(ge=0.0, le=1.0)] = None
    draft_id: Optional[str] = None
    draft_name: Optional[str] = None
    model_config = ConfigDict(extra="ignore")

