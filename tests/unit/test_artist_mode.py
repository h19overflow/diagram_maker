"""
Unit tests for artist mode orchestrator.

Tests parallel execution of chat agent and diagram generation.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.core.agentic_system.artist_mode import (
    invoke_artist_mode,
    invoke_chat_only,
    _invoke_chat_with_error_handling,
    _invoke_diagram_with_error_handling,
)
from src.api.schemas.chat import ChatResponse, GraphSnippet
from src.api.schemas.enums import DiagramType


@pytest.fixture
def sample_chat_response():
    """Create a sample chat response."""
    return ChatResponse(
        reply="QLoRA is a finetuning technique...",
        sources=["documentation"],
        score=0.75,
    )


@pytest.fixture
def sample_diagram_state():
    """Create a sample diagram state."""
    mock_diagram = MagicMock()
    mock_diagram.diagram_type = MagicMock()
    mock_diagram.diagram_type.value = "concept"

    return {
        "mermaid_diagram": "flowchart TD\n    node_001[...]",
        "final_diagram": mock_diagram,
        "error_message": None,
    }


class TestInvokeArtistMode:
    """Test cases for invoke_artist_mode orchestrator."""

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.artist_mode._invoke_chat_with_error_handling")
    @patch("src.core.agentic_system.artist_mode._invoke_diagram_with_error_handling")
    async def test_successful_parallel_execution(
        self, mock_diagram, mock_chat, sample_chat_response
    ):
        """Test successful parallel execution of chat and diagram."""
        # Setup
        mock_chat.return_value = sample_chat_response
        mock_diagram.return_value = (
            "flowchart TD\n    node_001[What is QLoRA?]",
            DiagramType.concept,
        )

        # Execute
        result = await invoke_artist_mode("What is QLoRA?")

        # Assert
        assert isinstance(result, ChatResponse)
        assert result.reply == sample_chat_response.reply
        assert result.sources == sample_chat_response.sources
        assert result.score == sample_chat_response.score
        assert result.graphs is not None
        assert len(result.graphs) == 1
        assert result.graphs[0].type == DiagramType.concept
        assert "flowchart TD" in result.graphs[0].mermaid

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.artist_mode._invoke_chat_with_error_handling")
    @patch("src.core.agentic_system.artist_mode._invoke_diagram_with_error_handling")
    async def test_chat_succeeds_diagram_fails(
        self, mock_diagram, mock_chat, sample_chat_response
    ):
        """Test when chat succeeds but diagram generation fails."""
        # Setup
        mock_chat.return_value = sample_chat_response
        mock_diagram.return_value = None  # Diagram failed

        # Execute
        result = await invoke_artist_mode("What is QLoRA?")

        # Assert
        assert isinstance(result, ChatResponse)
        assert result.reply == sample_chat_response.reply
        assert result.graphs is None  # No diagram

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.artist_mode._invoke_chat_with_error_handling")
    @patch("src.core.agentic_system.artist_mode._invoke_diagram_with_error_handling")
    async def test_both_systems_fail(self, mock_diagram, mock_chat):
        """Test when both chat and diagram fail."""
        # Setup
        error_response = ChatResponse(
            reply="Error occurred",
            sources=None,
            score=0.0,
        )
        mock_chat.return_value = error_response
        mock_diagram.return_value = None

        # Execute
        result = await invoke_artist_mode("test query")

        # Assert
        assert isinstance(result, ChatResponse)
        assert result.reply == "Error occurred"
        assert result.graphs is None


class TestInvokeChatOnly:
    """Test cases for invoke_chat_only function."""

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.artist_mode.invoke_chat_agent")
    async def test_successful_chat_only(self, mock_invoke, sample_chat_response):
        """Test successful chat-only invocation."""
        # Setup
        mock_invoke.return_value = sample_chat_response

        # Execute
        result = await invoke_chat_only("What is QLoRA?")

        # Assert
        assert isinstance(result, ChatResponse)
        assert result.reply == sample_chat_response.reply
        assert result.sources == sample_chat_response.sources
        mock_invoke.assert_called_once_with("What is QLoRA?")

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.artist_mode.invoke_chat_agent")
    async def test_chat_only_with_error(self, mock_invoke):
        """Test chat-only mode with error."""
        # Setup
        mock_invoke.side_effect = Exception("Chat agent error")

        # Execute
        result = await invoke_chat_only("test query")

        # Assert
        assert isinstance(result, ChatResponse)
        assert "error" in result.reply.lower()
        assert result.sources is None
        assert result.score == 0.0


class TestInvokeChatWithErrorHandling:
    """Test cases for _invoke_chat_with_error_handling."""

    @patch("src.core.agentic_system.artist_mode.invoke_chat_agent")
    def test_successful_chat_invocation(self, mock_invoke, sample_chat_response):
        """Test successful chat agent invocation."""
        # Setup
        mock_invoke.return_value = sample_chat_response

        # Execute
        result = _invoke_chat_with_error_handling("What is QLoRA?")

        # Assert
        assert isinstance(result, ChatResponse)
        assert result.reply == sample_chat_response.reply

    @patch("src.core.agentic_system.artist_mode.invoke_chat_agent")
    def test_chat_invocation_with_exception(self, mock_invoke):
        """Test chat invocation with exception."""
        # Setup
        mock_invoke.side_effect = Exception("Chat failed")

        # Execute
        result = _invoke_chat_with_error_handling("test query")

        # Assert
        assert isinstance(result, ChatResponse)
        assert "error" in result.reply.lower()
        assert result.score == 0.0


class TestInvokeDiagramWithErrorHandling:
    """Test cases for _invoke_diagram_with_error_handling."""

    @patch("src.core.agentic_system.artist_mode.diagram_graph")
    def test_successful_diagram_generation(self, mock_graph, sample_diagram_state):
        """Test successful diagram generation."""
        # Setup
        mock_graph.invoke.return_value = sample_diagram_state

        # Execute
        result = _invoke_diagram_with_error_handling("What is QLoRA?")

        # Assert
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2
        mermaid_code, diagram_type = result
        assert "flowchart TD" in mermaid_code
        assert diagram_type == DiagramType.concept

    @patch("src.core.agentic_system.artist_mode.diagram_graph")
    def test_diagram_with_error_message(self, mock_graph):
        """Test when diagram generation returns error message."""
        # Setup
        error_state = {
            "error_message": "Relevance check failed",
            "mermaid_diagram": None,
        }
        mock_graph.invoke.return_value = error_state

        # Execute
        result = _invoke_diagram_with_error_handling("test query")

        # Assert
        assert result is None

    @patch("src.core.agentic_system.artist_mode.diagram_graph")
    def test_diagram_with_no_mermaid_output(self, mock_graph):
        """Test when no mermaid diagram is generated."""
        # Setup
        empty_state = {
            "error_message": None,
            "mermaid_diagram": None,  # No diagram generated
            "final_diagram": None,
        }
        mock_graph.invoke.return_value = empty_state

        # Execute
        result = _invoke_diagram_with_error_handling("test query")

        # Assert
        assert result is None

    @patch("src.core.agentic_system.artist_mode.diagram_graph")
    def test_diagram_with_exception(self, mock_graph):
        """Test diagram generation with exception."""
        # Setup
        mock_graph.invoke.side_effect = Exception("Graph execution failed")

        # Execute
        result = _invoke_diagram_with_error_handling("test query")

        # Assert
        assert result is None

    @patch("src.core.agentic_system.artist_mode.diagram_graph")
    def test_diagram_defaults_to_flowchart(self, mock_graph):
        """Test that diagram type defaults to flowchart if not specified."""
        # Setup
        state_without_type = {
            "mermaid_diagram": "flowchart TD\n    node_001[Test]",
            "final_diagram": None,  # No diagram type
            "error_message": None,
        }
        mock_graph.invoke.return_value = state_without_type

        # Execute
        result = _invoke_diagram_with_error_handling("test query")

        # Assert
        assert result is not None
        mermaid_code, diagram_type = result
        assert diagram_type == DiagramType.flowchart


class TestParallelExecution:
    """Test cases for parallel execution behavior."""

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.artist_mode._invoke_chat_with_error_handling")
    @patch("src.core.agentic_system.artist_mode._invoke_diagram_with_error_handling")
    async def test_execution_timing(
        self, mock_diagram, mock_chat, sample_chat_response
    ):
        """Test that both systems are called (parallel execution)."""
        # Setup
        mock_chat.return_value = sample_chat_response
        mock_diagram.return_value = ("flowchart TD\n    test", DiagramType.flowchart)

        # Execute
        result = await invoke_artist_mode("test query")

        # Assert - both should be called
        mock_chat.assert_called_once_with("test query")
        mock_diagram.assert_called_once_with("test query")
        assert result is not None

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.artist_mode._invoke_chat_with_error_handling")
    @patch("src.core.agentic_system.artist_mode._invoke_diagram_with_error_handling")
    async def test_one_slow_one_fast(
        self, mock_diagram, mock_chat, sample_chat_response
    ):
        """Test that slow operations don't block the orchestrator."""
        # Setup - simulate one taking longer
        import asyncio

        async def slow_chat(*args):
            await asyncio.sleep(0.1)
            return sample_chat_response

        mock_chat.side_effect = slow_chat
        mock_diagram.return_value = ("flowchart TD\n    test", DiagramType.flowchart)

        # Execute
        result = await invoke_artist_mode("test query")

        # Assert - should still get both results
        assert result is not None
        assert result.reply == sample_chat_response.reply
        assert result.graphs is not None


class TestResponseCombination:
    """Test cases for combining chat and diagram responses."""

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.artist_mode._invoke_chat_with_error_handling")
    @patch("src.core.agentic_system.artist_mode._invoke_diagram_with_error_handling")
    async def test_response_includes_all_fields(
        self, mock_diagram, mock_chat
    ):
        """Test that response includes all expected fields."""
        # Setup
        chat_response = ChatResponse(
            reply="Test answer",
            sources=["doc1", "doc2"],
            score=0.85,
        )
        mock_chat.return_value = chat_response
        mock_diagram.return_value = (
            "flowchart TD\n    node[Test]",
            DiagramType.concept,
        )

        # Execute
        result = await invoke_artist_mode("test query")

        # Assert
        assert result.reply == "Test answer"
        assert result.sources == ["doc1", "doc2"]
        assert result.score == 0.85
        assert len(result.graphs) == 1
        assert result.graphs[0].type == DiagramType.concept

    @pytest.mark.asyncio
    @patch("src.core.agentic_system.artist_mode._invoke_chat_with_error_handling")
    @patch("src.core.agentic_system.artist_mode._invoke_diagram_with_error_handling")
    async def test_graph_snippet_structure(self, mock_diagram, mock_chat):
        """Test that GraphSnippet is structured correctly."""
        # Setup
        mock_chat.return_value = ChatResponse(reply="test", sources=None, score=0.0)
        mermaid_code = "flowchart LR\n    A[Start] --> B[End]"
        mock_diagram.return_value = (mermaid_code, DiagramType.flowchart)

        # Execute
        result = await invoke_artist_mode("test query")

        # Assert
        assert isinstance(result.graphs[0], GraphSnippet)
        assert result.graphs[0].type == DiagramType.flowchart
        assert result.graphs[0].mermaid == mermaid_code
