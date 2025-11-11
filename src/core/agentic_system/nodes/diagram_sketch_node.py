from src.core.agentic_system.graph_state import GraphState
from src.core.agentic_system.orchestrator.orchestrotor_agent import invoke_agent
from src.core.pipeline.vector_store import vector_store
from src.configs.rag_config import RAGConfig
from logging import getLogger
import asyncio

logger = getLogger(__name__)
config = RAGConfig()


def diagram_sketch_node(state: GraphState) -> GraphState:
    """
    Diagram sketch node that validates query relevance before generating diagram skeleton.

    Checks if the user's query is relevant to the documents in the vector store by
    examining similarity scores. If scores are below the threshold, returns an error.
    """
    try:
        question = state.user_input

        # Search with scores to check relevance
        results_with_scores = asyncio.run(
            vector_store.search_with_scores(question, k=10)
        )

        if len(results_with_scores) == 0:
            logger.warning(f"No documents found for query: {question}")
            return GraphState(
                error_message="No relevant documents found. Please ensure documents are uploaded and the query is related to the document content."
            )

        # Extract scores (second element of each tuple)
        scores = [score for _, score in results_with_scores]

        # Check the highest score (most relevant document)
        max_score = max(scores) if scores else 0.0
        avg_score = sum(scores) / len(scores) if scores else 0.0

        logger.info(
            f"Query relevance check - Max score: {max_score:.3f}, Avg score: {avg_score:.3f}, Threshold: {config.RELEVANCE_THRESHOLD}"
        )

        # Check if relevance is too low
        if max_score < config.RELEVANCE_THRESHOLD:
            logger.warning(
                f"Query '{question}' has low relevance (max score: {max_score:.3f} < threshold: {config.RELEVANCE_THRESHOLD})"
            )
            return GraphState(
                error_message=(
                    "The question is not sufficiently relevant to the documents in the knowledge base. "
                    "Please rephrase your question to better match the document content, or upload relevant documents."
                )
            )

        # Query is relevant, proceed with diagram generation
        logger.info("Query passed relevance check, proceeding with diagram generation")
        structured_response = invoke_agent(question)

        if structured_response is None:
            return GraphState(error_message="Failed to generate diagram skeleton")

        state.diagram_skeleton = structured_response
        return {"diagram_skeleton": structured_response, "error_message": None}

    except Exception as e:
        logger.error(f"Error in diagram sketch node: {e}")
        return GraphState(error_message=f"Error in diagram sketch node: {e}")


if __name__ == "__main__":
    state = GraphState(user_input="ًwhat is Qlora and how it works?")
    result = diagram_sketch_node(state)
    print(result['diagram_skeleton']['structured_response'])
