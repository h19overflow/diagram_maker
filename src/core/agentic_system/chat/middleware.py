"""
Middleware decorators for the chat agent.

Simple input validation and security checks using decorator pattern.
"""

from langchain.agents.middleware import before_model, AgentState
from langgraph.runtime import Runtime
from langchain.messages import AIMessage
from typing import Dict, Any
import logging
from src.core.agentic_system.chat.security import (
    validate_security,
    get_security_error_message,
)

logger = logging.getLogger(__name__)


@before_model
def security_check(state: AgentState, runtime: Runtime) -> Dict[str, Any] | None:
    """Check for security threats before processing.

    Args:
        state: Current agent state
        runtime: LangGraph runtime

    Returns:
        dict with messages and jump_to if threat detected, None otherwise
    """
    messages = state.get("messages", [])
    if not messages:
        return None

    last_message = messages[-1]
    query = last_message.content if hasattr(last_message, "content") else ""

    # Validate security
    security_result = validate_security(query)

    if not security_result["is_safe"]:
        threat_type = security_result["threat_type"]
        logger.error(
            f"Security threat detected: {threat_type} - {security_result['details']}"
        )
        return {
            "messages": [
                AIMessage(content=get_security_error_message(threat_type))
            ],
            "jump_to": "end",
        }

    return None


@before_model
def validate_input(state: AgentState, runtime: Runtime) -> Dict[str, Any] | None:
    """Validate input before sending to model.

    Args:
        state: Current agent state
        runtime: LangGraph runtime

    Returns:
        dict with messages and jump_to if validation fails, None otherwise
    """
    messages = state.get("messages", [])
    if not messages:
        return None

    last_message = messages[-1]
    query = last_message.content if hasattr(last_message, "content") else ""

    # Basic validation
    if not query or len(query.strip()) < 3:
        logger.warning("Query too short or empty")
        return {
            "messages": [
                AIMessage(
                    content="Please provide a more detailed question (at least 3 characters)."
                )
            ],
            "jump_to": "end",
        }

    return None


@before_model
def log_request(state: AgentState, runtime: Runtime) -> Dict[str, Any] | None:
    """Log incoming requests.

    Args:
        state: Current agent state
        runtime: LangGraph runtime

    Returns:
        None (doesn't modify state)
    """
    messages = state.get("messages", [])
    if messages:
        last_message = messages[-1]
        query = last_message.content if hasattr(last_message, "content") else ""
        logger.info(f"Processing query: {query[:100]}...")

    return None
