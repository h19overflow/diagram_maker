"""Text chunking utilities for the Hadith Scholar RAG pipeline."""

from __future__ import annotations

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from logging import getLogger

from src.configs.rag_config import RAGConfig
from src.core.pipeline.document_loader import load_document

logger = getLogger(__name__)


def _build_text_splitter(options: RAGConfig) -> RecursiveCharacterTextSplitter:
    # Recursive splitter respects language structure (paragraph -> sentence -> word)
    # which keeps Arabic Hadith passages coherent for downstream retrieval.
    return RecursiveCharacterTextSplitter(
        chunk_size=options.CHUNK_SIZE,
        chunk_overlap=options.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", ". ", "۔", " ", ""],
        add_start_index=True,
    )


def chunk_documents(documents: List[Document]) -> List[Document]:
    """Takes in a list of documents and chunks them into retrieval-ready chunks with metadata."""
    try:
        splitter = _build_text_splitter(RAGConfig())
        split_docs = splitter.split_documents(documents)
        return split_docs
    except Exception as e:
        logger.error(f"Error chunking documents: {e}")
        raise e


if __name__ == "__main__":
    documents = load_document(r"C:\Users\User\Projects\hadith_scholar\data\QLORA.pdf")
    chunked_docs = chunk_documents(documents)
    print(chunked_docs)
