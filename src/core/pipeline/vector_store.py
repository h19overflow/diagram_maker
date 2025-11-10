from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from src.configs.rag_config import RAGConfig
from prefect import task
from typing import List, Optional
from pathlib import Path
from logging import getLogger
from src.core.pipeline.document_loader import load_document
from src.core.pipeline.chunking import chunk_documents
import asyncio

logger = getLogger(__name__)


class VectorStore:
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize the vector store with persistence support.
        
        Args:
            persist_directory: Optional directory path to persist the vector store.
                              If None, uses VECTOR_STORE_PATH from config.
        """
        self.config = RAGConfig()
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Determine persistence path
        if persist_directory is None:
            persist_directory = self.config.VECTOR_STORE_PATH
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Try to load existing vector store, otherwise will create on first document addition
        self.vector_store = self._load_or_create_vector_store()
        if self.vector_store is None:
            logger.info(f"Vector store will be created at: {self.persist_directory} on first document addition")
        else:
            logger.info(f"Vector store initialized at: {self.persist_directory}")

    def _load_or_create_vector_store(self) -> Optional[FAISS]:
        """Load existing vector store from disk or return None to create new one."""
        index_path = self.persist_directory / "index.faiss"
        docstore_path = self.persist_directory / "index.pkl"
        
        try:
            if index_path.exists() and docstore_path.exists():
                logger.info("Loading existing vector store from disk")
                vector_store = FAISS.load_local(
                    str(self.persist_directory),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Successfully loaded existing vector store")
                return vector_store
            else:
                logger.info("No existing vector store found, will create on first document addition")
                return None
        except Exception as e:
            logger.warning(f"Error loading vector store, will create new one: {e}")
            return None

    def _save_vector_store(self):
        """Save the vector store to disk."""
        try:
            self.vector_store.save_local(
                str(self.persist_directory),
                index_name="index"
            )
            logger.info(f"Vector store saved to {self.persist_directory}")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            raise e

    @task(
        name="Add Documents",
        description="Add documents to the vector store",
        retries=3,
        retry_delay_seconds=10,
    )
    def add_documents(self, documents: List[Document]):
        """
        Add documents to the vector store and persist to disk.
        
        Args:
            documents: List of Document objects to add
        """
        try:
            if not documents:
                logger.warning("No documents provided to add")
                return
            
            # Create vector store if it doesn't exist yet
            if self.vector_store is None:
                logger.info("Creating new vector store with documents")
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
            else:
                # Add to existing store
                logger.info("Adding documents to existing vector store")
                self.vector_store.add_documents(documents)
            
            # Persist after adding documents
            self._save_vector_store()
            logger.info(f"Added {len(documents)} documents to vector store and persisted")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise e

    async def search(self, query: str, k: int = 10) -> List[Document]:
        """
        Search for similar documents in the vector store.
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of Document objects
        """
        try:
            if self.vector_store is None:
                logger.warning("Vector store is empty, returning empty results")
                return []
            
            return await self.vector_store.asimilarity_search(
                query=query,
                k=k,
            )
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise e

    async def search_with_scores(self, query: str, k: int = 10) -> List[tuple[Document, float]]:
        """
        Search for similar documents with similarity scores.
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of tuples containing (Document, score) pairs.
            Scores are similarity scores (higher = more similar).
            For cosine similarity, scores range from -1 to 1, typically 0 to 1.
        """
        try:
            if self.vector_store is None:
                logger.warning("Vector store is empty, returning empty results")
                return []
            
            return await self.vector_store.asimilarity_search_with_score(
                query=query,
                k=k,
            )
        except Exception as e:
            logger.error(f"Error searching with scores: {e}")
            raise e


# Singleton pattern with lazy initialization
_vector_store_instance: Optional[VectorStore] = None


def get_vector_store(persist_directory: Optional[str] = None) -> VectorStore:
    """
    Get or create the global VectorStore instance (singleton pattern).
    
    This provides the benefits of a global variable (single instance, fast access)
    while being more flexible and testable:
    - Lazy initialization (only creates when first accessed)
    - Can be reset for testing
    - Thread-safe with proper locking if needed
    
    Args:
        persist_directory: Optional directory path. Only used on first initialization.
                          Subsequent calls ignore this parameter.
    
    Returns:
        The global VectorStore instance
    """
    global _vector_store_instance
    
    if _vector_store_instance is None:
        logger.info("Initializing global VectorStore instance")
        _vector_store_instance = VectorStore(persist_directory=persist_directory)
    else:
        logger.debug("Returning existing VectorStore instance")
    
    return _vector_store_instance


def reset_vector_store():
    """
    Reset the global VectorStore instance.
    Useful for testing or when you need to reinitialize with different settings.
    """
    global _vector_store_instance
    _vector_store_instance = None
    logger.info("VectorStore instance reset")


# Convenience: Create instance on module import for immediate use
# This gives you the global variable behavior you want
vector_store = get_vector_store()


if __name__ == "__main__":
    # Example usage
    vector_store = get_vector_store()
    documents = load_document(r"C:\Users\User\Projects\hadith_scholar\data\QLORA.pdf")
    chunked_docs = chunk_documents(documents)
    with open('chunked_docs.txt', "w") as f:
        for doc in chunked_docs:
            f.write(doc.page_content + "\n")
    vector_store.add_documents(chunked_docs)

    results = asyncio.run(vector_store.search("What is the main idea of the document?", k=10))
    with open('results.txt', "w") as f:
        for result in results:
            f.write(result.page_content + "\n")