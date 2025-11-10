from prefect import flow
from src.core.pipeline.document_loader import load_document
from src.core.pipeline.chunking import chunk_documents
from src.core.pipeline.vector_store import get_vector_store
from logging import getLogger

logger = getLogger(__name__)

@flow(name="Ingestion Flow", description="Ingest documents into the vector store")
def ingestion_flow(file_path: str, vector_store=None):
    """
    Ingest documents into the vector store.
    
    Args:
        file_path: Path to the PDF file to ingest
        vector_store: Optional VectorStore instance. If None, uses the global singleton.
    """
    logger.info("Ingestion flow started")
    try:
        # Use global instance if not provided
        if vector_store is None:
            vector_store = get_vector_store()
        
        if file_path.endswith(".pdf"):
            documents = load_document(file_path)
            chunked_docs = chunk_documents(documents)
            vector_store.add_documents(chunked_docs)
        else:   
            logger.error("Invalid file type")
            raise ValueError("Invalid file type")
    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        raise e
    logger.info("Ingestion flow completed")