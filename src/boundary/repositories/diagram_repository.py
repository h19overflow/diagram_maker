"""
Diagram Repository

CRUD operations for the diagrams table.
Handles diagram creation, retrieval, updates, and search.
"""

from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from sqlalchemy.exc import SQLAlchemyError
from logging import getLogger

from src.boundary.models import Diagram

logger = getLogger(__name__)


class DiagramRepository:
    """Repository for diagram CRUD operations"""
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
    
    def create_diagram(
        self,
        user_id: UUID,
        s3_path: str,
        title: str,
        user_query: str,
        mermaid_code: str,
        description: Optional[str] = None,
        status: str = "draft"
    ) -> Diagram:
        """
        Create a new diagram.
        
        Args:
            user_id: User UUID (foreign key)
            s3_path: Full S3 path to the .mmd file
            title: Diagram title
            user_query: Original user query that generated this diagram
            mermaid_code: Generated Mermaid code
            description: Optional diagram description
            status: Diagram status (draft, published, archived)
            
        Returns:
            Created Diagram object
        """
        try:
            diagram = Diagram(
                user_id=user_id,
                s3_path=s3_path,
                title=title,
                description=description,
                user_query=user_query,
                mermaid_code=mermaid_code,
                status=status,
                version=1
            )
            self.session.add(diagram)
            self.session.commit()
            self.session.refresh(diagram)
            logger.info(f"Created diagram {diagram.diagram_id} for user {user_id}")
            return diagram
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error creating diagram: {e}")
            raise
    
    def get_diagram(self, diagram_id: UUID) -> Optional[Diagram]:
        """
        Get diagram by ID.
        
        Args:
            diagram_id: Diagram UUID
            
        Returns:
            Diagram object if found, None otherwise
        """
        try:
            return self.session.query(Diagram).filter(Diagram.diagram_id == diagram_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting diagram {diagram_id}: {e}")
            return None
    
    def get_user_diagrams(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Diagram]:
        """
        Get all diagrams for a user with optional filtering.
        
        Args:
            user_id: User UUID
            status: Optional status filter (draft, published, archived)
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            
        Returns:
            List of Diagram objects, ordered by created_at DESC
        """
        try:
            query = self.session.query(Diagram).filter(Diagram.user_id == user_id)
            
            # Apply status filter if provided
            if status:
                query = query.filter(Diagram.status == status)
            
            # Order by most recent first
            query = query.order_by(Diagram.created_at.desc())
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting diagrams for user {user_id}: {e}")
            return []
    
    def update_diagram(self, diagram_id: UUID, **kwargs) -> Optional[Diagram]:
        """
        Update diagram fields.
        
        Allowed fields: title, description, status, mermaid_code, version, s3_path
        
        Args:
            diagram_id: Diagram UUID
            **kwargs: Fields to update (title, description, status, mermaid_code, version, s3_path)
            
        Returns:
            Updated Diagram object if found, None otherwise
        """
        try:
            diagram = self.get_diagram(diagram_id)
            if not diagram:
                logger.warning(f"Diagram {diagram_id} not found for update")
                return None
            
            # Allowed fields for update
            allowed_fields = {"title", "description", "status", "mermaid_code", "version", "s3_path"}
            
            # Update only allowed fields
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(diagram, field, value)
            
            # Increment version if mermaid_code or other significant fields changed
            if "mermaid_code" in kwargs or "title" in kwargs:
                diagram.version += 1
            
            self.session.commit()
            self.session.refresh(diagram)
            logger.info(f"Updated diagram {diagram_id}")
            return diagram
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error updating diagram {diagram_id}: {e}")
            return None
    
    def delete_diagram(self, diagram_id: UUID) -> bool:
        """
        Delete diagram.
        
        Args:
            diagram_id: Diagram UUID
            
        Returns:
            True if deleted, False if diagram not found
        """
        try:
            diagram = self.get_diagram(diagram_id)
            if not diagram:
                logger.warning(f"Diagram {diagram_id} not found for deletion")
                return False
            
            self.session.delete(diagram)
            self.session.commit()
            logger.info(f"Deleted diagram {diagram_id}")
            return True
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error deleting diagram {diagram_id}: {e}")
            return False
    
    def search_diagrams(self, user_id: UUID, query: str) -> List[Diagram]:
        """
        Full-text search on title and description for a user's diagrams.
        
        Uses PostgreSQL's full-text search capabilities (matching schema.sql index).
        
        Args:
            user_id: User UUID
            query: Search query string
            
        Returns:
            List of Diagram objects matching the search, ordered by relevance
        """
        try:
            # Use PostgreSQL's to_tsvector for full-text search
            # This matches the index created in schema.sql: idx_diagrams_title_search
            search_vector = func.to_tsvector('english', Diagram.title + ' ' + func.coalesce(Diagram.description, ''))
            query_tsquery = func.plainto_tsquery('english', query)
            
            results = self.session.query(Diagram).filter(
                Diagram.user_id == user_id
            ).filter(
                search_vector.match(query_tsquery)
            ).order_by(
                func.ts_rank(search_vector, query_tsquery).desc()
            ).all()
            
            logger.info(f"Found {len(results)} diagrams matching '{query}' for user {user_id}")
            return results
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching diagrams for user {user_id}: {e}")
            # Fallback to simple LIKE search if full-text search fails
            try:
                search_pattern = f"%{query}%"
                return self.session.query(Diagram).filter(
                    Diagram.user_id == user_id
                ).filter(
                    or_(
                        Diagram.title.ilike(search_pattern),
                        Diagram.description.ilike(search_pattern)
                    )
                ).order_by(Diagram.created_at.desc()).all()
            except SQLAlchemyError as fallback_error:
                logger.error(f"Fallback search also failed: {fallback_error}")
                return []

