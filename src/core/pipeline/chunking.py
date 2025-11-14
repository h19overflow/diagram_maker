"""Text chunking utilities for the Hadith Scholar RAG pipeline."""

from __future__ import annotations

import os
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from logging import getLogger
from tqdm import tqdm
from src.configs.rag_config import RAGConfig
from src.core.pipeline.document_loader import load_document
from dotenv import load_dotenv

load_dotenv()
logger = getLogger(__name__)
def _build_text_splitter(options: RAGConfig) -> SemanticChunker:
    """Build a SemanticChunker with Bedrock embeddings and 80th percentile breakpoint."""
    embeddings = GoogleGenerativeAIEmbeddings(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        model="models/text-embedding-004",
    )
    return SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=80.0  # 80th percentile
    )


def _chunk_single_document(doc_info: Tuple[int, Document, RAGConfig]) -> Tuple[int, List[Document]]:
    """Process a single document and return its chunks with the original index.

    Args:
        doc_info: Tuple of (index, document, config)

    Returns:
        Tuple of (index, list of chunk documents)
    """
    doc_idx, doc, config = doc_info
    try:
        # Create a separate splitter instance for this thread
        splitter = _build_text_splitter(config)

        logger.debug(f"Processing document {doc_idx+1}: {len(doc.page_content)} characters")
        chunks = splitter.split_text(doc.page_content)

        # Create Document objects with metadata
        chunk_docs = []
        for chunk in chunks:
            chunk_doc = Document(
                page_content=chunk,
                metadata=doc.metadata.copy()
            )
            chunk_docs.append(chunk_doc)

        logger.debug(f"Document {doc_idx+1} produced {len(chunk_docs)} chunks")
        return doc_idx, chunk_docs
    except Exception as e:
        logger.error(f"Error processing document {doc_idx+1}: {e}")
        raise


def chunk_documents(documents: List[Document], max_workers: int = 20) -> List[Document]:
    """Takes in a list of documents and chunks them into retrieval-ready chunks with metadata.

    Uses semantic chunking with 80th percentile breakpoint to create semantically coherent chunks.
    Processes documents in parallel for improved performance.

    Args:
        documents: List of documents to chunk
        max_workers: Maximum number of parallel workers (default: 4)

    Returns:
        List of chunked documents
    """
    try:
        config = RAGConfig()

        # Show progress while chunking documents
        logger.info(f"Chunking {len(documents)} documents using semantic chunking (80th percentile breakpoint)")
        logger.info(f"Processing in parallel with {max_workers} workers...")

        # Prepare document info tuples with indices for maintaining order
        # Each thread will create its own splitter instance for thread safety
        doc_infos = [(i, doc, config) for i, doc in enumerate(documents)]

        # Process documents in parallel
        all_chunks = [None] * len(documents)  # Pre-allocate to maintain order

        with tqdm(total=len(documents), desc="Chunking documents", unit="doc") as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all documents for parallel processing
                future_to_doc = {
                    executor.submit(_chunk_single_document, doc_info): doc_info[0]
                    for doc_info in doc_infos
                }

                # Collect results as they complete
                for future in as_completed(future_to_doc):
                    doc_idx = future_to_doc[future]
                    try:
                        idx, chunk_docs = future.result()
                        all_chunks[idx] = chunk_docs
                        pbar.update(1)
                    except Exception as e:
                        logger.error(f"Failed to process document {doc_idx+1}: {e}")
                        raise

        # Flatten the list of chunk lists into a single list
        flattened_chunks = []
        for chunk_list in all_chunks:
            if chunk_list:
                flattened_chunks.extend(chunk_list)

        logger.info(f"Chunking produced {len(flattened_chunks)} total chunks from {len(documents)} documents")
        return flattened_chunks
    except Exception as e:
        logger.error(f"Error chunking documents: {e}")
        raise e


if __name__ == "__main__":
    documents = load_document(r"data\QLORA.pdf")
    chunked_docs = chunk_documents(documents)
    print(chunked_docs)
