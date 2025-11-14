"""
User Repository

CRUD operations for the users table.
Handles user creation, retrieval, and metadata updates.
"""

from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from logging import getLogger

from src.boundary.models import User

logger = getLogger(__name__)


class UserRepository:
    """Repository for user CRUD operations"""
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
    
    def get_user(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            User object if found, None otherwise
        """
        try:
            return self.session.query(User).filter(User.user_id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def get_or_create_user(self, user_id: UUID, user_metadata: Optional[dict] = None) -> User:
        """
        Get existing user or create new one (idempotent operation).
        
        This is the main method for handling anonymous users - if user_id exists,
        return it; otherwise create a new user record.
        
        Args:
            user_id: User UUID (from frontend localStorage)
            user_metadata: Optional metadata dictionary
            
        Returns:
            User object (existing or newly created)
        """
        try:
            # Try to get existing user
            user = self.get_user(user_id)
            
            if user:
                logger.debug(f"User {user_id} already exists")
                return user
            
            # Create new user
            user = User(
                user_id=user_id,
                user_metadata=user_metadata or {}
            )
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            logger.info(f"Created new user {user_id}")
            return user
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error in get_or_create_user for {user_id}: {e}")
            raise
    
    def create_user(self, user_id: Optional[UUID] = None, user_metadata: Optional[dict] = None) -> User:
        """
        Create a new user.
        
        Args:
            user_id: Optional UUID (if None, database will generate one)
            user_metadata: Optional metadata dictionary
            
        Returns:
            Created User object
        """
        try:
            user = User(
                user_id=user_id,
                user_metadata=user_metadata or {}
            )
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            logger.info(f"Created user {user.user_id}")
            return user
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    def update_user_metadata(self, user_id: UUID, metadata: dict) -> Optional[User]:
        """
        Update user metadata.
        
        Args:
            user_id: User UUID
            metadata: Dictionary of metadata to update (will merge with existing)
            
        Returns:
            Updated User object if found, None otherwise
        """
        try:
            user = self.get_user(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for metadata update")
                return None
            
            # Merge metadata (update existing keys, keep others)
            if user.user_metadata:
                user.user_metadata.update(metadata)
            else:
                user.user_metadata = metadata
            
            self.session.commit()
            self.session.refresh(user)
            logger.info(f"Updated metadata for user {user_id}")
            return user
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error updating user metadata for {user_id}: {e}")
            return None
    
    def delete_user(self, user_id: UUID) -> bool:
        """
        Delete user (cascades to diagrams due to foreign key constraint).
        
        Args:
            user_id: User UUID
            
        Returns:
            True if deleted, False if user not found
        """
        try:
            user = self.get_user(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for deletion")
                return False
            
            self.session.delete(user)
            self.session.commit()
            logger.info(f"Deleted user {user_id} and associated diagrams")
            return True
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

