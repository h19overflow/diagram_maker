"""
Pytest configuration and fixtures for the test suite.

Provides common fixtures for:
- Mock vector stores and documents
- Sample chat responses
- Mock agents and graph states
- Test environment configuration
"""

import pytest
from unittest.mock import MagicMock
from langchain_core.documents import Document


# Configure pytest-asyncio (uncomment if pytest-asyncio is installed)
# pytest_plugins = ("pytest_asyncio",)


@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    return [
        Document(
            page_content="QLoRA is a quantization technique for fine-tuning LLMs",
            metadata={"source": "qlora.pdf", "page": 1},
        ),
        Document(
            page_content="It reduces memory usage by using 4-bit quantization",
            metadata={"source": "qlora.pdf", "page": 2},
        ),
        Document(
            page_content="QLoRA maintains performance while reducing resources",
            metadata={"source": "qlora.pdf", "page": 3},
        ),
    ]


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store for testing."""
    mock_vs = MagicMock()
    mock_vs.vector_store = MagicMock()
    return mock_vs


@pytest.fixture
def sample_chat_response():
    """Create a sample ChatResponse for testing."""
    from src.api.schemas.chat import ChatResponse

    return ChatResponse(
        reply="QLoRA is a finetuning technique that reduces memory usage...",
        sources=["documentation"],
        score=0.75,
    )


@pytest.fixture
def mock_agent():
    """Create a mock LangChain agent."""
    agent = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Test response from agent"
    agent.invoke.return_value = {"messages": [mock_message]}
    return agent


@pytest.fixture
def sample_graph_state():
    """Create a sample GraphState for diagram testing."""
    from src.core.agentic_system.diagrams.graph_state import GraphState

    return GraphState(
        user_input="What is QLoRA?",
        error_message=None,
    )


# TODO: Additional fixtures to implement:
# - Create fixtures for database sessions and connections
# - Create fixtures for S3 client mocking
# - Set up test environment variables and configuration

