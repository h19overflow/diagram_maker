from src.core.agentic_system.graph_state import GraphState
from src.core.pipeline.vector_store import VectorStore
from langchain_core.documents import Document
from typing import Dict, List
from logging import getLogger
import asyncio
from src.core.pipeline.vector_store import vector_store

logger = getLogger(__name__)


async def retrieval_node(state: GraphState) -> GraphState:
    """
    Retrieval node that searches for documents for each node title in the diagram skeleton.
    Populates context_docs as a dictionary mapping node titles to their corresponding documents.
    """
    try:
        if state.diagram_skeleton is None or not state.diagram_skeleton.nodes:
            logger.warning("No diagram skeleton or nodes found in state")
            return GraphState(error_message="No diagram skeleton found for retrieval")
        
        # Dictionary to store title -> documents mapping
        context_docs_dict: Dict[str, List[Document]] = {}
        
        # Search for documents for each node title
        for node in state.diagram_skeleton.nodes:
            title = node.title
            logger.info(f"Searching for documents with query: {title}")
            
            try:
                # Perform async search
                documents = await vector_store.search(query=title, k=10)
                context_docs_dict[title] = documents
                logger.info(f"Found {len(documents)} documents for title: {title}")
            except Exception as e:
                logger.error(f"Error searching for title '{title}': {e}")
                context_docs_dict[title] = []  # Empty list on error
        
        logger.info(f"Retrieved documents for {len(context_docs_dict)} node titles")
        
        return {
            "context_docs": context_docs_dict,
            "error_message": None
        }
    except Exception as e:
        logger.error(f"Error in retrieval node: {e}")
        return GraphState(error_message=f"Error in retrieval node: {e}")


def retrieval_node_sync(state: GraphState) -> GraphState:
    """
    Synchronous wrapper for the async retrieval node.
    """
    try:
        return asyncio.run(retrieval_node(state))
    except Exception as e:
        logger.error(f"Error in retrieval node sync wrapper: {e}")
        return GraphState(error_message=f"Error in retrieval node: {e}")


if __name__ == "__main__":
    from src.core.agentic_system.respone_formats import NodeTitles, HierarchicalNodeTitle
    
    # Create a test state with diagram skeleton
    test_nodes = [
        HierarchicalNodeTitle(
            node_id="node_001",
            title="What are the major systems in the human body?",
            hierarchy_level=0,
            parent_node_id=None,
            children_node_ids=["node_002", "node_003"]
        ),
        HierarchicalNodeTitle(
            node_id="node_002",
            title="What are the primary components of the circulatory system?",
            hierarchy_level=1,
            parent_node_id="node_001",
            children_node_ids=[]
        )
    ]
    
    test_skeleton = NodeTitles(nodes=test_nodes)
    state = GraphState(
        user_input="I want to create a diagram of the human body",
        diagram_skeleton=test_skeleton
    )
    
    result = retrieval_node_sync(state)
    print(f"Retrieved documents for {len(result['context_docs']) if result['context_docs'] else 0} titles")
    if result['context_docs']:
        for title, docs in result['context_docs'].items():
            print(f"  {title}: {docs} documents")
