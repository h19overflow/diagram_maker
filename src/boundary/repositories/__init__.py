"""
Repository module for data access layer

Exports repository classes for database CRUD operations.
"""

from src.boundary.repositories.user_repository import UserRepository
from src.boundary.repositories.diagram_repository import DiagramRepository

__all__ = ["UserRepository", "DiagramRepository"]
