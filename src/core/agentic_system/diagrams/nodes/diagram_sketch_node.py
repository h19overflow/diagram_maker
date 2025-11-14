from src.core.agentic_system.diagrams.graph_state import GraphState
from src.core.agentic_system.diagrams.nodes.utils.node_utils import validate_query_relevance
from src.core.agentic_system.diagrams.orchestrator.orchestrotor_agent import invoke_agent
from logging import getLogger
import asyncio

logger = getLogger(__name__)


def diagram_sketch_node(state) -> dict:
    """
    Diagram sketch node that validates query relevance before generating diagram skeleton.

    Checks if the user's query is relevant to the documents in the vector store by
    examining similarity scores. If scores are below the threshold, returns an error.
    """
    try:
        # Handle both dict and GraphState object access
        question = (
            state.get("user_input") if isinstance(state, dict) else state.user_input
        )

        # Validate query relevance
        is_relevant, error_message = asyncio.run(validate_query_relevance(question))
        if not is_relevant:
            return {"error_message": error_message}

        # Query is relevant, proceed with diagram generation
        logger.info("Query passed relevance check, proceeding with diagram generation")
        structured_response = invoke_agent(question)

        if structured_response is None:
            return {"error_message": "Failed to generate diagram skeleton"}

        return {"diagram_skeleton": structured_response, "error_message": None}

    except Exception as e:
        logger.error(f"Error in diagram sketch node: {e}")
        return {"error_message": f"Error in diagram sketch node: {e}"}


if __name__ == "__main__":
    state = GraphState(user_input="ًwhat is Qlora and how it works?")
    result = diagram_sketch_node(state)
    print(result["diagram_skeleton"])
