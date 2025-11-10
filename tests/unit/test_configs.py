"""
Unit tests for configuration modules.

Tests cover:
- RAGConfig validation and defaults
- APIConfig validation and defaults
- Environment variable loading
- Type validation
- Required fields
"""

import os
import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict
from src.configs import RAGConfig, APIConfig


class TestRAGConfig:
    """Test RAGConfig class"""
    
    def test_rag_config_defaults(self, monkeypatch):
        """Test that RAGConfig has correct default values"""
        # Disable .env file loading for tests
        monkeypatch.setenv("_PYDANTIC_SETTINGS_SKIP_ENV_FILE", "1")
        # Create config with only required field
        config = RAGConfig(_env_file=None, S3_BUCKET_NAME="test-bucket")
        
        # LLM defaults
        assert config.BEDROCK_MODEL_ID == "amazon.nova-lite-v1:0"
        assert config.BEDROCK_TEMPERATURE == 0.7
        assert config.BEDROCK_MAX_TOKENS == 4096
        
        # Embedding defaults
        assert config.EMBEDDING_MODEL_NAME == "intfloat/multilingual-e5-base"
        assert config.EMBEDDING_DEVICE == "cpu"
        assert config.EMBEDDING_BATCH_SIZE == 32
        assert config.EMBEDDING_DIMENSION == 768
        
        # Chunking defaults
        assert config.CHUNK_SIZE == 1000
        assert config.CHUNK_OVERLAP == 200
        
        # Retrieval defaults
        assert config.BM25_TOP_K == 20
        assert config.VECTOR_TOP_K == 20
        assert config.BM25_WEIGHT == 0.7
        assert config.VECTOR_WEIGHT == 0.3
        assert config.HYBRID_TOP_K == 10
        
        # S3
        assert config.S3_BUCKET_NAME == "test-bucket"
        assert config.S3_PRESIGNED_URL_EXPIRATION == 3600
    
    def test_rag_config_required_field(self, monkeypatch):
        """Test that S3_BUCKET_NAME is required"""
        monkeypatch.setenv("_PYDANTIC_SETTINGS_SKIP_ENV_FILE", "1")
        with pytest.raises(ValidationError) as exc_info:
            RAGConfig(_env_file=None)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("S3_BUCKET_NAME",) for error in errors)
    
    def test_rag_config_env_override(self, monkeypatch):
        """Test that environment variables override defaults"""
        monkeypatch.setenv("_PYDANTIC_SETTINGS_SKIP_ENV_FILE", "1")
        monkeypatch.setenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
        monkeypatch.setenv("BEDROCK_TEMPERATURE", "0.5")
        monkeypatch.setenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-large")
        monkeypatch.setenv("CHUNK_SIZE", "512")
        monkeypatch.setenv("S3_BUCKET_NAME", "my-bucket")
        
        config = RAGConfig(_env_file=None)
        
        assert config.BEDROCK_MODEL_ID == "anthropic.claude-3-sonnet-20240229-v1:0"
        assert config.BEDROCK_TEMPERATURE == 0.5
        assert config.EMBEDDING_MODEL_NAME == "intfloat/multilingual-e5-large"
        assert config.CHUNK_SIZE == 512
        assert config.S3_BUCKET_NAME == "my-bucket"
    
    def test_rag_config_type_validation(self, monkeypatch):
        """Test that type validation works correctly"""
        monkeypatch.setenv("_PYDANTIC_SETTINGS_SKIP_ENV_FILE", "1")
        # Valid types
        config = RAGConfig(
            _env_file=None,
            S3_BUCKET_NAME="test",
            BEDROCK_TEMPERATURE=0.5,
            BEDROCK_MAX_TOKENS=2048,
            EMBEDDING_BATCH_SIZE=64,
            CHUNK_SIZE=500,
            BM25_TOP_K=10
        )
        assert isinstance(config.BEDROCK_TEMPERATURE, float)
        assert isinstance(config.BEDROCK_MAX_TOKENS, int)
        assert isinstance(config.EMBEDDING_BATCH_SIZE, int)
        
        # Invalid types should raise ValidationError
        with pytest.raises(ValidationError):
            RAGConfig(
                _env_file=None,
                S3_BUCKET_NAME="test",
                BEDROCK_TEMPERATURE="not-a-float"
            )
        
        with pytest.raises(ValidationError):
            RAGConfig(
                _env_file=None,
                S3_BUCKET_NAME="test",
                CHUNK_SIZE="not-an-int"
            )
    
    def test_rag_config_hybrid_weights_sum(self, monkeypatch):
        """Test that hybrid weights can be configured (they don't need to sum to 1.0)"""
        monkeypatch.setenv("_PYDANTIC_SETTINGS_SKIP_ENV_FILE", "1")
        config = RAGConfig(
            _env_file=None,
            S3_BUCKET_NAME="test",
            BM25_WEIGHT=0.8,
            VECTOR_WEIGHT=0.2
        )
        assert config.BM25_WEIGHT == 0.8
        assert config.VECTOR_WEIGHT == 0.2


class TestAPIConfig:
    """Test APIConfig class"""
    
    def test_api_config_defaults(self, monkeypatch):
        """Test that APIConfig has correct default values"""
        monkeypatch.setenv("_PYDANTIC_SETTINGS_SKIP_ENV_FILE", "1")
        config = APIConfig(_env_file=None)
        
        # Server defaults
        assert config.API_HOST == "0.0.0.0"
        assert config.API_PORT == 8000
        assert config.API_RELOAD is False
        
        # CORS defaults
        assert config.API_CORS_ORIGINS == ["*"]
        
        # Rate limiting
        assert config.API_RATE_LIMIT == 100
        
        # Logging
        assert config.LOG_LEVEL == "INFO"
    
    def test_api_config_env_override(self, monkeypatch):
        """Test that environment variables override defaults"""
        monkeypatch.setenv("_PYDANTIC_SETTINGS_SKIP_ENV_FILE", "1")
        monkeypatch.setenv("API_HOST", "127.0.0.1")
        monkeypatch.setenv("API_PORT", "9000")
        monkeypatch.setenv("API_RELOAD", "true")
        monkeypatch.setenv("API_RATE_LIMIT", "200")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        
        config = APIConfig(_env_file=None)
        
        assert config.API_HOST == "127.0.0.1"
        assert config.API_PORT == 9000
        assert config.API_RELOAD is True
        assert config.API_RATE_LIMIT == 200
        assert config.LOG_LEVEL == "DEBUG"
    
    def test_api_config_type_validation(self, monkeypatch):
        """Test that type validation works correctly"""
        monkeypatch.setenv("_PYDANTIC_SETTINGS_SKIP_ENV_FILE", "1")
        # Valid types
        config = APIConfig(
            _env_file=None,
            API_PORT=8080,
            API_RELOAD=True,
            API_RATE_LIMIT=50
        )
        assert isinstance(config.API_PORT, int)
        assert isinstance(config.API_RELOAD, bool)
        assert isinstance(config.API_RATE_LIMIT, int)
        
        # Invalid types should raise ValidationError
        with pytest.raises(ValidationError):
            APIConfig(_env_file=None, API_PORT="not-an-int")
        
        with pytest.raises(ValidationError):
            APIConfig(_env_file=None, API_RELOAD="not-a-bool")
    
    def test_api_config_cors_origins(self, monkeypatch):
        """Test CORS origins configuration"""
        monkeypatch.setenv("_PYDANTIC_SETTINGS_SKIP_ENV_FILE", "1")
        # Default
        config = APIConfig(_env_file=None)
        assert config.API_CORS_ORIGINS == ["*"]
        
        # Custom list
        config = APIConfig(_env_file=None, API_CORS_ORIGINS=["http://localhost:3000", "https://example.com"])
        assert len(config.API_CORS_ORIGINS) == 2
        assert "http://localhost:3000" in config.API_CORS_ORIGINS


class TestConfigIntegration:
    """Test configuration integration and usage"""
    
    def test_both_configs_can_coexist(self, monkeypatch):
        """Test that both configs can be instantiated together"""
        monkeypatch.setenv("_PYDANTIC_SETTINGS_SKIP_ENV_FILE", "1")
        rag_config = RAGConfig(_env_file=None, S3_BUCKET_NAME="test-bucket")
        api_config = APIConfig(_env_file=None)
        
        assert rag_config.S3_BUCKET_NAME == "test-bucket"
        assert api_config.API_PORT == 8000
    
    def test_config_imports(self):
        """Test that configs can be imported from package"""
        from src.configs import RAGConfig, APIConfig
        
        assert RAGConfig is not None
        assert APIConfig is not None
    
    def test_config_serialization(self, monkeypatch):
        """Test that configs can be serialized (for logging/debugging)"""
        monkeypatch.setenv("_PYDANTIC_SETTINGS_SKIP_ENV_FILE", "1")
        rag_config = RAGConfig(_env_file=None, S3_BUCKET_NAME="test-bucket")
        api_config = APIConfig(_env_file=None)
        
        # Should be able to convert to dict
        rag_dict = rag_config.model_dump()
        api_dict = api_config.model_dump()
        
        assert isinstance(rag_dict, dict)
        assert isinstance(api_dict, dict)
        assert "S3_BUCKET_NAME" in rag_dict
        assert "API_PORT" in api_dict
    
    def test_config_json_serialization(self, monkeypatch):
        """Test that configs can be serialized to JSON"""
        monkeypatch.setenv("_PYDANTIC_SETTINGS_SKIP_ENV_FILE", "1")
        rag_config = RAGConfig(_env_file=None, S3_BUCKET_NAME="test-bucket")
        api_config = APIConfig(_env_file=None)
        
        # Should be able to convert to JSON
        rag_json = rag_config.model_dump_json()
        api_json = api_config.model_dump_json()
        
        assert isinstance(rag_json, str)
        assert isinstance(api_json, str)
        assert "test-bucket" in rag_json
        assert "8000" in api_json

