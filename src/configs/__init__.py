"""
Configuration module for Hadith Scholar RAG System

This module provides two main configuration classes:
- RAGConfig: All RAG pipeline related settings (models, retrieval, chunking, S3)
- APIConfig: All API related settings (server, CORS, streaming, security)

Note: Infrastructure configurations (AWS credentials, database connections, etc.)
are managed via Terraform and environment variables.
"""

from .rag_config import RAGConfig
from .api_config import APIConfig

__all__ = ["RAGConfig", "APIConfig"]

