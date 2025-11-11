"""
RAG (Retrieval-Augmented Generation) Configuration

This module contains all configuration settings related to the RAG pipeline:
- LLM and embedding model settings
- Retrieval parameters (BM25, vector, hybrid fusion)
- Text chunking parameters
- S3 configuration for document storage
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()   

class RAGConfig(BaseSettings):
    """Configuration for RAG pipeline components"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields from .env (infrastructure configs managed by Terraform)
    )
    
    # ========== LLM Configuration (AWS Bedrock) ==========
    # Note: AWS credentials and region should be set via Terraform/environment
    BEDROCK_MODEL_ID: str = Field(default="amazon.nova-lite-v1:0")
    BEDROCK_TEMPERATURE: float = Field(default=0.7)
    BEDROCK_MAX_TOKENS: int = Field(default=4096)
    
    # ========== Embedding Model Configuration (AWS Bedrock) ==========
    BEDROCK_EMBEDDING_MODEL_ID: str = Field(
        default="amazon.titan-embed-text-v2:0",
        description="AWS Bedrock embedding model ID (supports multilingual including Arabic)"
    )
    BEDROCK_REGION: str = Field(
        default="ap-southeast-2",
        description="AWS region for Bedrock service"
    )
    EMBEDDING_DIMENSION: int = Field(default=1024, description="Titan v2 embedding dimension: 1024")
    
    # ========== Text Chunking Configuration ==========
    CHUNK_SIZE: int = Field(default=5128, description="Chunk size in tokens (500-1000 recommended)")
    CHUNK_OVERLAP: int = Field(default=300, description="Overlap between chunks in tokens (100-200 recommended)")
    
    # ========== Retrieval Configuration ==========
    # BM25 Configuration
    BM25_TOP_K: int = Field(default=20, description="Top-k results from BM25 retrieval")
    
    # Vector Search Configuration
    VECTOR_TOP_K: int = Field(default=20, description="Top-k results from vector similarity search")
    
    # Hybrid Fusion Configuration
    BM25_WEIGHT: float = Field(default=0.7, description="Weight for BM25 scores in hybrid fusion")
    VECTOR_WEIGHT: float = Field(default=0.3, description="Weight for vector scores in hybrid fusion")
    HYBRID_TOP_K: int = Field(default=10, description="Final top-k results after hybrid fusion")
    
    # ========== S3 Configuration ==========
    # Note: S3 bucket name, region, and credentials should be set via Terraform
    S3_BUCKET_NAME: str = Field(..., description="S3 bucket for storing PDF documents")
    S3_PRESIGNED_URL_EXPIRATION: int = Field(
        default=3600,
        description="Presigned URL expiration time in seconds (default: 1 hour)"
    )
    
    # ========== Vector Store Persistence Configuration ==========
    VECTOR_STORE_PATH: str = Field(
        default="./vector_store",
        description="Path to persist the vector store index and documents"
    )
    
    # ========== Relevance Threshold Configuration ==========
    RELEVANCE_THRESHOLD: float = Field(
        default=0.5,
        description="Minimum similarity score threshold for document relevance (0.0 to 1.0). "
                   "Queries with scores below this threshold are considered not relevant."
    )


