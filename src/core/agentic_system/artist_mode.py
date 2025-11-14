"""
Artist Mode orchestrator - parallel execution of chat and diagram generation.

This module provides the "artist mode" feature where users get both:
1. Text answer from the chat agent
2. Visual diagram from the diagram generation system

Both systems run in parallel for optimal performance.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Optional
import logging
from src.core.agentic_system.chat.chat_agent import invoke_agent as invoke_chat_agent
from src.core.agentic_system.diagrams.graph import diagram_graph
from src.core.agentic_system.diagrams.graph_state import GraphState
from src.api.schemas.chat import ChatResponse, GraphSnippet
from src.api.schemas.enums import DiagramType

logger = logging.getLogger(__name__)


async def invoke_artist_mode(message: str) -> ChatResponse:
    """Invoke both chat agent and diagram generation in parallel.

    Args:
        message: The user's query/message

    Returns:
        ChatResponse with both text reply and visual diagram (if successful)

    This function orchestrates parallel execution of:
    - Chat agent for text-based answer
    - Diagram generation for visual representation
    """
    logger.info(f"Artist mode invoked for message: {message[:50]}...")

    # Run both systems in parallel using ThreadPoolExecutor
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=2) as executor:
        # Execute chat agent
        chat_future = loop.run_in_executor(
            executor, _invoke_chat_with_error_handling, message
        )

        # Execute diagram generation
        diagram_future = loop.run_in_executor(
            executor, _invoke_diagram_with_error_handling, message
        )

        # Wait for both to complete
        chat_response, diagram_result = await asyncio.gather(
            chat_future, diagram_future, return_exceptions=False
        )

    logger.info("Both chat and diagram generation completed")

    # Build the combined response
    response = ChatResponse(
        reply=chat_response.reply,
        sources=chat_response.sources,
        score=chat_response.score,
        graphs=None,  # Will be populated if diagram succeeded
    )

    # Add diagram if generation was successful
    if diagram_result is not None:
        mermaid_code, diagram_type = diagram_result
        response.graphs = [GraphSnippet(type=diagram_type, mermaid=mermaid_code)]
        logger.info(f"Added diagram to response (type: {diagram_type})")
    else:
        logger.warning("Diagram generation failed or returned no result")

    return response


def _invoke_chat_with_error_handling(message: str):
    """Invoke chat agent with error handling.

    Args:
        message: The user's message

    Returns:
        ChatResponse from the chat agent
    """
    try:
        logger.info("Invoking chat agent...")
        return invoke_chat_agent(message)
    except Exception as e:
        logger.error(f"Chat agent failed: {e}")
        # Return fallback response
        from src.api.schemas.chat import ChatResponse

        return ChatResponse(
            reply=f"I encountered an error processing your question: {str(e)}",
            sources=None,
            score=0.0,
        )


def _invoke_diagram_with_error_handling(
    message: str,
) -> Optional[Tuple[str, DiagramType]]:
    """Invoke diagram generation with error handling.

    Args:
        message: The user's message

    Returns:
        Tuple of (mermaid_code, diagram_type) or None if failed
    """
    try:
        logger.info("Invoking diagram generation...")

        # Create initial state
        initial_state = GraphState(user_input=message)

        # Run the graph
        final_state = diagram_graph.invoke(initial_state)

        # Check for errors
        if final_state.get("error_message"):
            logger.warning(
                f"Diagram generation returned error: {final_state['error_message']}"
            )
            return None

        # Extract mermaid diagram
        mermaid_code = final_state.get("mermaid_diagram")
        if not mermaid_code:
            logger.warning("No mermaid diagram generated")
            return None

        # Extract diagram type (default to flowchart)
        final_diagram = final_state.get("final_diagram")
        if final_diagram and hasattr(final_diagram, "diagram_type"):
            diagram_type = DiagramType(final_diagram.diagram_type.value)
        else:
            diagram_type = DiagramType.flowchart
            logger.info("Defaulting to flowchart diagram type")

        logger.info(f"Diagram generated successfully (type: {diagram_type})")
        return (mermaid_code, diagram_type)

    except Exception as e:
        logger.error(f"Diagram generation failed: {e}", exc_info=True)
        return None


async def invoke_chat_only(message: str) -> ChatResponse:
    """Invoke only the chat agent (no diagram generation).

    Args:
        message: The user's message

    Returns:
        ChatResponse with text reply only

    This is used when artist_mode=False.
    """
    logger.info(f"Chat-only mode invoked for message: {message[:50]}...")

    try:
        chat_response = invoke_chat_agent(message)
        logger.info("Chat agent completed successfully")
        return chat_response
    except Exception as e:
        logger.error(f"Chat agent failed: {e}")
        return ChatResponse(
            reply=f"I encountered an error processing your question: {str(e)}",
            sources=None,
            score=0.0,
        )


if __name__ == "__main__":
    """Test artist mode with a sample query."""
    import asyncio

    async def test_artist_mode():
        print("\n" + "=" * 80)
        print("ARTIST MODE TEST")
        print("=" * 80)

        test_query = "What is QLoRA and how does it work?"
        print(f"\nQuery: {test_query}\n")

        # Test artist mode (parallel execution)
        print("Testing artist mode (chat + diagram)...")
        result = await invoke_artist_mode(test_query)

        print("\n--- Results ---")
        print(f"Reply: {result.reply[:200]}...")
        print(f"Sources: {result.sources}")
        print(f"Score: {result.score}")
        print(f"Graphs: {len(result.graphs) if result.graphs else 0} diagram(s)")

        if result.graphs:
            for i, graph in enumerate(result.graphs):
                print(f"\nDiagram {i+1}:")
                print(f"  Type: {graph.type}")
                print(f"  Mermaid (first 200 chars): {graph.mermaid[:200]}...")

    # Run the test
    asyncio.run(test_artist_mode())
