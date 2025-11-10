from src.core.agentic_system.graph_state import GraphState
from src.core.agentic_system.helpers.helper_agent import invoke_agent


def helper_populating_node(state: GraphState) -> GraphState:
    try:
        question = state.user_input
        context = state.context_docs
        structured_response = invoke_agent(question, context)["structured_response"]
        if structured_response is None:
            return GraphState(error_message="Failed to generate helper response")
        state.helper_response = structured_response
        return {"helper_response": structured_response, "error_message": None}
    except Exception as e:
        return GraphState(error_message=f"Error in helper populating node: {e}")
    