"""
API Configuration

This module contains all configuration settings related to the FastAPI application:
- Server settings (host, port)
- CORS configuration
- Streaming configuration
- Rate limiting and security
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any
from dotenv import load_dotenv

load_dotenv()

class APIConfig(BaseSettings):
    """Configuration for FastAPI application"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields from .env (infrastructure configs managed by Terraform)
    )
    
    # ========== Server Configuration ==========
    API_HOST: str = Field(default="0.0.0.0", description="API server host")
    API_PORT: int = Field(default=8001, description="API server port")
    API_RELOAD: bool = Field(default=False, description="Enable auto-reload in development")
    
    # ========== CORS Configuration ==========
    # Use Any to prevent Pydantic Settings from auto JSON parsing, validator converts to list[str]
    API_CORS_ORIGINS: Any = Field(default="*", description="Allowed CORS origins (comma-separated or JSON list)")
    
    @field_validator("API_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from string (JSON or comma-separated) or return list as-is"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            if not v or not v.strip():
                return ["*"]
            v = v.strip()
            # Try JSON format first
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Otherwise, split by comma
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            return origins if origins else ["*"]
        # Fallback
        return ["*"]
    # ========== Rate Limiting ==========
    API_RATE_LIMIT: int = Field(
        default=100,
        description="Rate limit: requests per minute per IP"
    )
    # ========== Logging ==========
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
