"""
RDS Database Connection and Session Management

This module handles SQLAlchemy database connection, engine setup, and session management
for PostgreSQL RDS database.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from logging import getLogger
from typing import Generator

load_dotenv()

logger = getLogger(__name__)


class DatabaseConfig(BaseSettings):
    """Configuration for PostgreSQL RDS database connection"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    # Database connection settings
    DB_HOST: str = Field(default="localhost", description="RDS database host")
    DB_PORT: int = Field(default=5432, description="Database port")
    DB_NAME: str = Field(default="diagram_maker", description="Database name")
    DB_USER: str = Field(default="diagram_maker_admin", description="Database username")
    DB_PASSWORD: str = Field(default="postgres", description="Database password")
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL with psycopg2 driver"""
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Initialize database config
db_config = DatabaseConfig()

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    db_config.database_url,
    pool_size=5,  # Number of connections to maintain in pool
    max_overflow=10,  # Additional connections beyond pool_size
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Set to True for SQL query logging (debug mode)
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Usage:
        with get_session() as session:
            # Use session here
            pass
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def check_connection() -> bool:
    """
    Check if database connection is healthy.
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("Database connection check successful")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def init_db():
    """
    Initialize database connection and verify it's working.
    Call this at application startup.
    """
    try:
        if check_connection():
            logger.info(f"Database connection established to {db_config.DB_HOST}:{db_config.DB_PORT}/{db_config.DB_NAME}")
        else:
            logger.error("Failed to establish database connection")
            raise ConnectionError("Cannot connect to database")
    except SQLAlchemyError as e:
        logger.error(f"Database connection check failed: {e}")
        raise ConnectionError("Cannot connect to database") from e

if __name__ == "__main__":
    import sys
    # Configure basic logging to see output
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print(f"Attempting to connect to: {db_config.DB_HOST}:{db_config.DB_PORT}/{db_config.DB_NAME}")
    print(f"Connection string: postgresql+psycopg2://{db_config.DB_USER}:***@{db_config.DB_HOST}:{db_config.DB_PORT}/{db_config.DB_NAME}")

    if check_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        sys.exit(1)