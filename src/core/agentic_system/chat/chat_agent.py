"""
Chat agent with RAG capabilities and fallback logic.

This module provides:
- Simple chat agent using gemini-2.5-flash-lite
- Vector store integration for context retrieval
- Fallback when similarity scores are low
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from langchain.tools import tool
from src.core.pipeline.vector_store import get_vector_store
from src.core.agentic_system.chat.consts import (
    get_system_prompt,
    get_user_prompt_template,
    get_fallback_message,
    SIMILARITY_THRESHOLD,
    MODEL_NAME,
)
from src.core.agentic_system.chat.middleware import (
    security_check,
    validate_input,
    log_request,
)
from src.api.schemas.chat import ChatResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@tool
def retrieve_context(query: str) -> dict:
    """Retrieve relevant context from documentation using vector store.

    Args:
        query: The user's question

    Returns:
        dict with context, similarity_score, and is_relevant flag
    """
    try:
        logger.info(f"Retrieving context for query: {query[:50]}...")
        vector_store = get_vector_store()

        # Search for relevant documents
        results = vector_store.vector_store.similarity_search_with_score(query, k=3)

        if not results:
            logger.warning("No results found in vector store")
            return {
                "context": "",
                "similarity_score": 0.0,
                "is_relevant": False,
                "documents_retrieved": 0,
            }

        # Extract context and calculate average similarity
        contexts = [doc.page_content for doc, score in results]
        scores = [float(score) for doc, score in results]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Note: FAISS returns L2 distance, lower is better
        # Convert to similarity score (invert and normalize)
        similarity_score = max(0.0, 1.0 - (avg_score / 2.0))

        is_relevant = similarity_score >= SIMILARITY_THRESHOLD

        logger.info(
            f"Retrieved {len(results)} documents with avg similarity: {similarity_score:.3f}"
        )

        return {
            "context": "\n\n".join(contexts),
            "similarity_score": similarity_score,
            "is_relevant": is_relevant,
            "documents_retrieved": len(results),
        }

    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return {
            "context": "",
            "similarity_score": 0.0,
            "is_relevant": False,
            "documents_retrieved": 0,
            "error": str(e),
        }


def get_agent():
    """Get the chat agent with retrieval tool.

    Returns:
        The configured agent
    """
    try:
        agent = create_agent(
            model=MODEL_NAME,
            tools=[retrieve_context],
            middleware=[validate_input, log_request],
        )
        return agent
    except Exception as e:
        logger.error(f"Error creating chat agent: {e}")
        return None


def invoke_agent(query: str) -> ChatResponse:
    """Invoke the chat agent and return structured response.

    Args:
        query: The user's question

    Returns:
        ChatResponse with reply, sources, and score
    """
    try:
        agent = get_agent()
        if agent is None:
            raise ValueError("Failed to initialize agent")

        logger.info(f"Invoking chat agent for query: {query[:50]}...")

        # First, retrieve context to check relevance
        retrieval_result = retrieve_context.invoke({"query": query})

        # If context is not relevant, return fallback message
        if not retrieval_result["is_relevant"]:
            logger.warning(
                f"Context not relevant (score: {retrieval_result['similarity_score']:.3f})"
            )
            return ChatResponse(
                reply=get_fallback_message(query),
                sources=None,
                score=retrieval_result["similarity_score"],
            )

        # Build prompt with context
        context = retrieval_result["context"]
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", get_system_prompt()),
                ("user", get_user_prompt_template().format(context=context, input=query)),
            ]
        )

        # Invoke agent
        prompt_invoked = prompt.invoke({"context": context, "input": query})
        response = agent.invoke(prompt_invoked)

        # Extract response text from agent response
        if isinstance(response, dict):
            # Get the last message from the messages list
            messages = response.get("messages", [])
            if messages:
                last_message = messages[-1]
                reply = last_message.content if hasattr(last_message, "content") else str(last_message)
            else:
                reply = response.get("output", str(response))
        elif hasattr(response, "content"):
            reply = response.content
        else:
            reply = str(response)

        logger.info(f"Generated response: {len(reply)} characters")

        return ChatResponse(
            reply=reply,
            sources=["documentation"],
            score=retrieval_result["similarity_score"],
        )

    except Exception as e:
        logger.error(f"Error invoking chat agent: {e}")
        return ChatResponse(
            reply=f"I encountered an error processing your question: {str(e)}",
            sources=None,
            score=0.0,
        )


if __name__ == "__main__":
    # Trial run
    test_queries = [
        "What is QLoRA?",
        "How does quantization work?",
        "What is the meaning of life?",  # Should trigger fallback
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        response = invoke_agent(query)
        print(f"\nReply: {response.reply}")
        print(f"Sources: {response.sources}")
        print(f"Score: {response.score:.3f}")
