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


class GenerateDiagramRequest(BaseModel):
    user_input: str = Field(..., description="User query for diagram generation")
    user_id: str = Field(..., description="User ID from browser localStorage (UUID format)")


class GenerateDiagramResponse(BaseModel):
    mermaid_diagram: str = Field(..., description="Generated Mermaid diagram")
    mermaid_filepath: Optional[str] = Field(None, description="Path where diagram was saved")
    diagram_id: Optional[str] = Field(None, description="UUID of the created diagram in database")
    error_message: Optional[str] = Field(None, description="Error message if generation failed")

