from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from src.core.agentic_system.respone_formats import IRSDiagramResponse, NodeTitles
from langchain_core.documents import Document


class GraphState(BaseModel):
    user_input: Optional[str] = Field(description="The user input",default=None)
    context_docs: Optional[Dict[str, List[Document]]] = Field(
        description="The context documents as a dictionary mapping titles to documents",default=None
    )
    diagram_skeleton: Optional[NodeTitles] = Field(
        description="The diagram skeleton",default=None
    )
    final_diagram: Optional[IRSDiagramResponse] = Field(description="The final diagram",default=None)
    error_message: Optional[str] = Field(description="The error message",default=None)
