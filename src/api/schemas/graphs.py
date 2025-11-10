from pydantic import BaseModel, Field
from typing import Optional
from .enums import DiagramType, LayoutStyle, Complexity


class GenerateVariantRequest(BaseModel):
    diagram_type: DiagramType = Field(default=DiagramType.flowchart)
    layout_style: LayoutStyle = Field(default=LayoutStyle.compact)
    complexity: Complexity = Field(default=Complexity.simple)
    mermaid: Optional[str] = None  # supply existing graph to mutate
    seed: Optional[int] = None  # deterministic variants


class GraphVariantResponse(BaseModel):
    mermaid: str


class GraphRenderRequest(BaseModel):
    mermaid: str


class GraphRenderResponse(BaseModel):
    svg: str

