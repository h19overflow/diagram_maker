"""Module for response formats of the agentic system"""

from pydantic import BaseModel, Field
from typing import Optional
from src.api.schemas.enums import DiagramType


class HierarchicalNodeTitle(BaseModel):
    """Hierarchical node with title as a question and structural metadata"""
    node_id: str = Field(description="Unique identifier for the node")
    title: str = Field(description="The node title as a specific question for RAG search")
    hierarchy_level: int = Field(
        description="The depth/level in the hierarchy (0 = root/top level, increases for deeper nodes)"
    )
    parent_node_id: Optional[str] = Field(
        default=None, description="The ID of the parent node in the hierarchy, None if root"
    )
    children_node_ids: list[str] = Field(
        default_factory=list, description="List of child node IDs in the hierarchy"
    )


class NodeTitles(BaseModel):
    """Collection of hierarchical nodes for the diagram"""
    nodes: list[HierarchicalNodeTitle] = Field(
        description="List of nodes with hierarchical structure"
    )


class Nodes(BaseModel):
    """Node model for the diagram with full structure information"""
    id: list[str] = Field(description="List of unique node identifiers")
    title: list[str] = Field(
        description="List of node titles (questions) corresponding to node IDs"
    )
    hierarchy_level: list[int] = Field(
        description="List of hierarchy levels for each node"
    )
    parent_node_id: list[Optional[str]] = Field(
        description="List of parent node IDs for each node (None for root nodes)"
    )
    description: Optional[list[str]] = Field(
        default=None, description="Optional descriptions for each node"
    )


class Edges(BaseModel):
    """Edge model for the diagram with source and target relationships"""
    source: list[str] = Field(description="List of source node IDs")
    target: list[str] = Field(description="List of target node IDs")
    description: Optional[list[str]] = Field(
        default=None, description="Optional descriptions for each edge"
    )


class IRSDiagramResponse(BaseModel):
    """Complete hierarchical diagram response with nodes and edges"""
    diagram_type: DiagramType = Field(description="The type of the diagram")
    title: str = Field(description="The title of the diagram")
    nodes: list[Nodes] = Field(description="The nodes of the diagram with hierarchy")
    edges: list[Edges] = Field(description="The edges connecting nodes")



class HelperResponse(BaseModel):
    """Helper response for the agentic system"""
    response: str = Field(description="The response from the helper agent", default="")
    sources: list[str] = Field(description="The sources from the helper agent")
    score: Optional[float] = Field(description="The score from the helper agent", default=None)