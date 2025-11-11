from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_aws import BedrockEmbeddings
from src.configs.rag_config import RAGConfig
from typing import List, Optional
from pathlib import Path
from logging import getLogger, basicConfig, INFO
from src.core.pipeline.document_loader import load_document
from src.core.pipeline.chunking import chunk_documents
import asyncio
from tqdm import tqdm
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import numpy as np
import faiss
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging if not already configured
basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

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
        # Verify AWS credentials and Bedrock access before initializing embeddings
        self._verify_aws_credentials()
        logger.info(f"Initializing BedrockEmbeddings with model_id={self.config.BEDROCK_EMBEDDING_MODEL_ID}, region={self.config.BEDROCK_REGION}")
        self.embeddings = BedrockEmbeddings(
            model_id=self.config.BEDROCK_EMBEDDING_MODEL_ID,
            region_name=self.config.BEDROCK_REGION
        )
        
        # Test the embeddings client with a simple query
        self._test_embeddings_client()
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

    def _verify_aws_credentials(self):
        """Verify AWS credentials are configured."""
        try:
            logger.info("Verifying AWS credentials...")
            session = boto3.Session(region_name=self.config.BEDROCK_REGION)
            credentials = session.get_credentials()
            if credentials is None:
                raise NoCredentialsError("AWS credentials not found. Please configure AWS credentials.")
            logger.info("AWS credentials found")
            # Test Bedrock access (client creation validates credentials)
            boto3.client('bedrock-runtime', region_name=self.config.BEDROCK_REGION)
            logger.info(f"Bedrock client initialized for region: {self.config.BEDROCK_REGION}")
        except NoCredentialsError as e:
            logger.error(f"AWS credentials error: {e}")
            raise RuntimeError(
                "AWS credentials not configured. Please set up AWS credentials using one of:\n"
                "1. AWS CLI: aws configure\n"
                "2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY\n"
                "3. IAM role (if running on EC2)"
            ) from e
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"AWS client error: {error_code} - {e}")
            raise RuntimeError(f"Failed to initialize AWS Bedrock client: {error_code}") from e
        except Exception as e:
            logger.error(f"Unexpected error verifying AWS credentials: {e}")
            raise

    def _test_embeddings_client(self):
        """Test the embeddings client with a simple query to ensure it's working."""
        try:
            logger.info("Testing BedrockEmbeddings client with a test query...")
            test_text = "test"
            embedding = self.embeddings.embed_query(test_text)

            if embedding is None or len(embedding) == 0:
                raise RuntimeError("Embeddings client returned empty result")

            logger.info(f"✓ BedrockEmbeddings client is working correctly (embedding dimension: {len(embedding)})")
        except Exception as e:
            logger.error(f"Failed to test BedrockEmbeddings client: {e}")
            raise RuntimeError(
                f"BedrockEmbeddings client test failed. Please check:\n"
                f"1. AWS credentials are configured correctly\n"
                f"2. Bedrock service is enabled in region {self.config.BEDROCK_REGION}\n"
                f"3. Model {self.config.BEDROCK_EMBEDDING_MODEL_ID} is available\n"
                f"4. Network connectivity to AWS\n"
                f"Error: {e}"
            ) from e

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

    def add_documents(self, documents: List[Document], batch_size: int = 200, max_workers: int = 2):
        """
        Add documents to the vector store and persist to disk.
        
        Args:
            documents: List of Document objects to add
            batch_size: Number of documents to process in each batch (default: 200)
            max_workers: Maximum number of parallel API calls (default: 5)
        """
        try:
            if not documents:
                logger.warning("No documents provided to add")
                return
            
            total_docs = len(documents)
            logger.info(f"Starting to add {total_docs} documents to vector store (batch_size={batch_size})")

            # Create vector store if it doesn't exist yet
            if self.vector_store is None:
                logger.info("Creating new vector store with documents")
                # Embed all documents first in batches for better performance
                logger.info(f"Embedding documents in batches (batch_size={batch_size}, max_workers={max_workers})...")
                texts = [doc.page_content for doc in documents]
                embeddings = self._embed_documents_in_batches(texts, batch_size, max_workers=max_workers)

                # Create FAISS index manually from pre-computed embeddings
                logger.info("Creating FAISS index from embeddings...")
                embedding_dim = len(embeddings[0])
                index = faiss.IndexFlatL2(embedding_dim)

                # Convert embeddings to numpy array
                embeddings_array = np.array(embeddings).astype('float32')
                index.add(embeddings_array)

                # Create FAISS vector store with the index and documents
                from langchain_community.docstore.in_memory import InMemoryDocstore
                docstore = InMemoryDocstore()
                index_to_docstore_id = {}

                # Add documents to docstore
                for i, doc in enumerate(documents):
                    docstore.add({str(i): doc})
                    index_to_docstore_id[i] = str(i)

                self.vector_store = FAISS(
                    embedding_function=self.embeddings,
                    index=index,
                    docstore=docstore,
                    index_to_docstore_id=index_to_docstore_id
                )

                logger.info(f"Vector store created with {len(documents)} documents")
            else:
                # Add to existing store in batches
                logger.info("Adding documents to existing vector store")
                self._add_documents_in_batches(documents, batch_size, start_idx=0, total=total_docs)

            # Persist after adding documents
            logger.info("Saving vector store to disk...")
            self._save_vector_store()
            logger.info(f"Successfully added {total_docs} documents to vector store and persisted")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise e

    def _embed_documents_in_batches(self, texts: List[str], batch_size: int = 100, max_workers: int = 2) -> List[List[float]]:
        """
        Embed documents in batches with parallel processing for better performance.

        Args:
            texts: List of text strings to embed
            batch_size: Number of documents per batch
            max_workers: Maximum number of parallel API calls (default: 5)

        Returns:
            List of embedding vectors
        """
        # Split texts into batches
        batches = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            batches.append((batch_num, batch_texts))

        num_batches = len(batches)
        logger.info(f"Processing {num_batches} batches with {max_workers} parallel workers...")

        # Store results in a list, indexed by batch number
        results = [None] * num_batches
        all_embeddings = []

        def embed_batch(batch_info):
            """Helper function to embed a single batch."""
            batch_num, batch_texts = batch_info
            try:
                logger.info(f"Embedding batch {batch_num}/{num_batches} ({len(batch_texts)} documents)...")
                batch_embeddings = self.embeddings.embed_documents(batch_texts)
                logger.info(f"Batch {batch_num} embedded successfully")
                return batch_num - 1, batch_embeddings  # Return 0-indexed position
            except Exception as e:
                logger.error(f"Error embedding batch {batch_num}: {e}")
                raise e

        # Process batches in parallel using ThreadPoolExecutor
        with tqdm(total=len(texts), desc="Embedding documents", unit="doc") as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all batches for parallel processing
                future_to_batch = {executor.submit(embed_batch, batch_info): batch_info for batch_info in batches}

                # Collect results as they complete
                for future in as_completed(future_to_batch):
                    batch_info = future_to_batch[future]
                    batch_num, batch_texts = batch_info
                    try:
                        batch_idx, batch_embeddings = future.result()
                        results[batch_idx] = batch_embeddings
                        pbar.update(len(batch_texts))
                    except Exception as e:
                        logger.error(f"Batch {batch_num} failed: {e}")
                        raise e

        # Combine results in order
        for batch_embeddings in results:
            if batch_embeddings is not None:
                all_embeddings.extend(batch_embeddings)

        logger.info(f"Successfully embedded {len(all_embeddings)} documents")
        return all_embeddings

    def _add_documents_in_batches(self, documents: List[Document], batch_size: int, start_idx: int = 0, total: int = 0):
        """Add documents in batches with progress logging."""
        num_batches = (len(documents) + batch_size - 1) // batch_size

        # Create overall progress bar
        with tqdm(total=len(documents), desc="Adding documents", unit="doc", initial=start_idx) as overall_pbar:
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                current_idx = start_idx + i

                logger.info(f"Processing batch {batch_num}/{num_batches} ({len(batch)} documents, "
                           f"total progress: {current_idx + len(batch)}/{total})...")

                try:
                    # Show batch progress
                    with tqdm(total=len(batch), desc=f"Batch {batch_num}/{num_batches}", unit="doc", leave=False) as batch_pbar:
                        self.vector_store.add_documents(batch)
                        batch_pbar.update(len(batch))

                    overall_pbar.update(len(batch))
                    logger.info(f"Batch {batch_num} completed successfully")
                except Exception as e:
                    logger.error(f"Error processing batch {batch_num}: {e}")
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
    from src.core.pipeline.retrieval import Retriever

    print("Starting vector store creation")
    vector_store = get_vector_store()
    documents = load_document(r"data\React_paper.pdf")
    chunked_docs = chunk_documents(documents)
    print("Chunking documents")
    with open('chunked_docs.txt', "w") as f:
        for doc in chunked_docs:
            f.write(doc.page_content + "\n")
    print("Adding documents to vector store")
    vector_store.add_documents(chunked_docs)
    print("Documents added to vector store")

    # Use Retriever for search operations
    retriever = Retriever(vector_store.vector_store)
    results = asyncio.run(retriever.search("What is the main idea of the document?", k=10))
    with open('results.txt', "w") as f:
        for result in results:
            f.write(result.page_content + "\n")