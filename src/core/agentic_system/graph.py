"""
LangGraph implementation for the diagram generation agentic system.

This graph orchestrates the flow from user input to final diagram:
1. Diagram Sketch Node - Validates query and generates diagram skeleton
2. Retrieval Node - Retrieves relevant documents for each node
3. Helper Populating Node - Generates descriptions and creates final diagram
"""

from langgraph.graph import StateGraph, END
from src.core.agentic_system.graph_state import GraphState
from src.core.agentic_system.nodes.diagram_sketch_node import diagram_sketch_node
from src.core.agentic_system.nodes.retrieval_node import retrieval_node_sync
from src.core.agentic_system.nodes.helper_populating_node import helper_populating_node
from logging import getLogger

logger = getLogger(__name__)


def route_after_sketch(state) -> str:
    """
    Route after diagram sketch node.

    Args:
        state: Current graph state (dict or GraphState)

    Returns:
        Next node name or END
    """
    # Handle both dict and GraphState object access
    error_message = state.get("error_message") if isinstance(state, dict) else state.error_message
    diagram_skeleton = state.get("diagram_skeleton") if isinstance(state, dict) else state.diagram_skeleton

    if error_message:
        logger.error(f"Graph stopped due to error: {error_message}")
        return END

    if diagram_skeleton:
        logger.info("Routing to retrieval node")
        return "retrieval"

    logger.error("No diagram skeleton generated")
    return END


def route_after_retrieval(state) -> str:
    """
    Route after retrieval node.

    Args:
        state: Current graph state (dict or GraphState)

    Returns:
        Next node name or END
    """
    # Handle both dict and GraphState object access
    error_message = state.get("error_message") if isinstance(state, dict) else state.error_message
    context_docs = state.get("context_docs") if isinstance(state, dict) else state.context_docs

    if error_message:
        logger.error(f"Graph stopped due to error: {error_message}")
        return END

    if context_docs:
        logger.info("Routing to helper populating node")
        return "helper_populating"

    logger.error("No context documents retrieved")
    return END


def route_after_helper(state) -> str:
    """
    Route after helper populating node.

    Args:
        state: Current graph state (dict or GraphState)

    Returns:
        END (always end after helper populating)
    """
    # Handle both dict and GraphState object access
    error_message = state.get("error_message") if isinstance(state, dict) else state.error_message
    final_diagram = state.get("final_diagram") if isinstance(state, dict) else state.final_diagram

    if error_message:
        logger.error(f"Graph stopped due to error: {error_message}")
    elif final_diagram:
        logger.info("Graph completed successfully")
    else:
        logger.warning("No final diagram generated")

    return END


def create_diagram_graph() -> StateGraph:
    """
    Create and configure the LangGraph for diagram generation.

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("diagram_sketch", diagram_sketch_node)
    workflow.add_node("retrieval", retrieval_node_sync)
    workflow.add_node("helper_populating", helper_populating_node)

    # Set entry point
    workflow.set_entry_point("diagram_sketch")

    # Add conditional edges
    # When using a list, the routing function can return either a node name or END
    workflow.add_conditional_edges(
        "diagram_sketch",
        route_after_sketch,
        ["retrieval", END],
    )

    workflow.add_conditional_edges(
        "retrieval",
        route_after_retrieval,
        ["helper_populating", END],
    )

    workflow.add_conditional_edges(
        "helper_populating",
        route_after_helper,
        [END],
    )

    # Compile the graph
    app = workflow.compile()

    return app


# Create the graph instance
diagram_graph = create_diagram_graph()


if __name__ == "__main__":
    """
    Example usage of the diagram generation graph.
    Note: LangGraph outputs a dictionary even when initialized with a Pydantic BaseModel.
    """
    from src.core.agentic_system.graph_state import GraphState

    # Create initial state with user input
    initial_state = GraphState(
        user_input="What is Qlora and how does it work?"
    )

    print("=" * 80)
    print("Starting Diagram Generation Graph")
    print("=" * 80)
    print(f"User Input: {initial_state.user_input}\n")

    try:
        # Run the graph - output is a dictionary, not a Pydantic object
        final_state = diagram_graph.invoke(initial_state)

        # Check for errors - use dictionary access
        if final_state.get("error_message"):
            print(f"\n❌ Error: {final_state['error_message']}")
        else:
            print("\n✅ Graph execution completed successfully!")
            diagram_skeleton = final_state.get("diagram_skeleton")
            context_docs = final_state.get("context_docs")
            final_diagram = final_state.get("final_diagram")

            print(f"\nDiagram Skeleton Nodes: {len(diagram_skeleton.nodes) if diagram_skeleton else 0}")
            print(f"Context Documents: {len(context_docs) if context_docs else 0} node titles")

            if final_diagram:
                print("\nFinal Diagram:")
                print(f"  Title: {final_diagram.title}")
                print(f"  Type: {final_diagram.diagram_type}")
                if final_diagram.nodes:
                    nodes_obj = final_diagram.nodes[0]
                    print(f"  Nodes: {len(nodes_obj.id)}")
                    print(f"  Edges: {len(final_diagram.edges[0].source) if final_diagram.edges else 0}")

                    # Print node details
                    print("\n  Node Details:")
                    for i, node_id in enumerate(nodes_obj.id):
                        print(f"    - {node_id}: {nodes_obj.title[i]}")
                        if nodes_obj.description and nodes_obj.description[i]:
                            desc_preview = nodes_obj.description[i][:100] + "..." if len(nodes_obj.description[i]) > 100 else nodes_obj.description[i]
                            print(f"      Description: {desc_preview}")
            # Print Mermaid diagram info
            mermaid_diagram = final_state.get("mermaid_diagram")
            mermaid_filepath = final_state.get("mermaid_filepath")
            if mermaid_diagram:
                print("\n📊 Mermaid Diagram Generated:")
                print(f"  File saved to: {mermaid_filepath if mermaid_filepath else 'Not saved'}")
                print("\n  Preview (first 500 chars):")
                print("  " + "\n  ".join(mermaid_diagram[:500].split("\n")))
                if len(mermaid_diagram) > 500:
                    print("  ...")

    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
