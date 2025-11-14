"""
SQLAlchemy Models for Diagram Maker Database

This module defines the database models matching the schema.sql structure:
- User: Stores user information (no authentication, just tracking)
- Diagram: Stores diagram drafts with metadata and S3 paths
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, CheckConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from uuid import uuid4

Base = declarative_base()


class User(Base):
    """
    User model matching the users table in schema.sql.
    
    Stores minimal user information for tracking diagram ownership.
    No authentication - just anonymous user tracking.
    """
    __tablename__ = "users"
    
    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
    user_metadata = Column(
        JSONB,
        default={},
        nullable=False
    )
    
    # Relationship to diagrams
    diagrams = relationship("Diagram", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(user_id={self.user_id})>"


class Diagram(Base):
    """
    Diagram model matching the diagrams table in schema.sql.
    
    Stores diagram drafts with metadata, S3 paths, and mermaid code.
    """
    __tablename__ = "diagrams"
    
    diagram_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True
    )
    s3_path = Column(
        Text,
        nullable=False
    )
    title = Column(
        String(255),
        nullable=False
    )
    description = Column(
        Text,
        nullable=True
    )
    user_query = Column(
        Text,
        nullable=False
    )
    mermaid_code = Column(
        Text,
        nullable=False
    )
    status = Column(
        String(50),
        default="draft",
        nullable=False,
        index=True
    )
    version = Column(
        Integer,
        default=1,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        index=True
    )
    
    # Add check constraint for status
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="diagrams_status_check"
        ),
    )
    
    # Relationship to user
    user = relationship("User", back_populates="diagrams")
    
    def __repr__(self):
        return f"<Diagram(diagram_id={self.diagram_id}, title={self.title}, status={self.status})>"

