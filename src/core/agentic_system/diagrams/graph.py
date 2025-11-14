"""
LangGraph implementation for the diagram generation agentic system.

This graph orchestrates the flow from user input to final diagram:
1. Diagram Sketch Node - Validates query and generates diagram skeleton
2. Retrieval Node - Retrieves relevant documents for each node
3. Helper Populating Node - Generates descriptions and creates final diagram
4. Mermaid Generation Node - Converts final diagram to Mermaid syntax
5. Mermaid File Save Node - Saves Mermaid diagram to local file
6. Mermaid S3 Upload Node - Uploads Mermaid diagram to S3 for later retrieval
7. Database Persistence Node - Persists diagram metadata to database
"""

from langgraph.graph import StateGraph, END
from src.core.agentic_system.diagrams.graph_state import GraphState
from src.core.agentic_system.diagrams.nodes.diagram_sketch_node import diagram_sketch_node
from src.core.agentic_system.diagrams.nodes.retrieval_node import retrieval_node_sync
from src.core.agentic_system.diagrams.nodes.helper_populating_node import helper_populating_node
from src.core.agentic_system.diagrams.nodes.mermaid_generation_node import mermaid_generation_node
from src.core.agentic_system.diagrams.nodes.mermaid_file_save_node import mermaid_file_save_node
from src.core.agentic_system.diagrams.nodes.mermaid_s3_upload_node import mermaid_s3_upload_node
from src.core.agentic_system.diagrams.nodes.database_persistence_node import database_persistence_node
from logging import getLogger

logger = getLogger(__name__)


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
    workflow.add_node("mermaid_generation", mermaid_generation_node)
    workflow.add_node("mermaid_file_save", mermaid_file_save_node)
    workflow.add_node("mermaid_s3_upload", mermaid_s3_upload_node)
    workflow.add_node("database_persistence", database_persistence_node)

    # Set entry point
    workflow.set_entry_point("diagram_sketch")

    # Add direct edges - simple linear flow
    workflow.add_edge("diagram_sketch", "retrieval")
    workflow.add_edge("retrieval", "helper_populating")
    workflow.add_edge("helper_populating", "mermaid_generation")
    workflow.add_edge("mermaid_generation", "mermaid_file_save")
    workflow.add_edge("mermaid_file_save", "mermaid_s3_upload")
    workflow.add_edge("mermaid_s3_upload", "database_persistence")
    workflow.add_edge("database_persistence", END)

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
    from src.core.agentic_system.diagrams.graph_state import GraphState

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
