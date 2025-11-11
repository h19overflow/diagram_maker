"""Text chunking utilities for the Hadith Scholar RAG pipeline."""

from __future__ import annotations

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import TokenTextSplitter
from logging import getLogger
from tqdm import tqdm
import tiktoken

from src.configs.rag_config import RAGConfig
from src.core.pipeline.document_loader import load_document

logger = getLogger(__name__)


def _count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count tokens in text using tiktoken."""
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Error counting tokens with {encoding_name}, falling back to character-based estimate: {e}")
        # Fallback: approximate 1 token = 4 characters
        return len(text) // 4


def _build_text_splitter(options: RAGConfig) -> TokenTextSplitter:
    # Use TokenTextSplitter for accurate token-based chunking
    # cl100k_base is used by GPT-4 and is a good general-purpose tokenizer
    return TokenTextSplitter(
        chunk_size=options.CHUNK_SIZE,
        chunk_overlap=options.CHUNK_OVERLAP,
        encoding_name="cl100k_base",
    )


def _merge_small_chunks(chunks: List[Document], min_tokens: int) -> List[Document]:
    """Merge chunks that are below the minimum token size with adjacent chunks."""
    if not chunks:
        return chunks

    merged_chunks = []
    i = 0

    with tqdm(total=len(chunks), desc="Merging small chunks", unit="chunk", leave=False) as pbar:
        while i < len(chunks):
            current_chunk = chunks[i]
            current_tokens = _count_tokens(current_chunk.page_content)

            # If chunk is already large enough, keep it as is
            if current_tokens >= min_tokens:
                merged_chunks.append(current_chunk)
                i += 1
                pbar.update(1)
                continue

            # Otherwise, try to merge with next chunk(s)
            merged_content = current_chunk.page_content
            merged_metadata = current_chunk.metadata.copy()
            merged_tokens = current_tokens
            j = i + 1

            # Merge with subsequent chunks until we reach minimum size or run out of chunks
            while merged_tokens < min_tokens and j < len(chunks):
                next_chunk = chunks[j]
                next_tokens = _count_tokens(next_chunk.page_content)

                # Merge content
                merged_content += "\n\n" + next_chunk.page_content
                merged_tokens += next_tokens

                # Merge metadata (keep common keys, prefer first chunk's values)
                for key, value in next_chunk.metadata.items():
                    if key not in merged_metadata:
                        merged_metadata[key] = value

                j += 1

            # Create merged document
            merged_doc = Document(
                page_content=merged_content,
                metadata=merged_metadata
            )
            merged_chunks.append(merged_doc)

            # Log if we had to merge
            if j > i + 1:
                logger.debug(f"Merged {j - i} chunks (total tokens: {merged_tokens})")

            pbar.update(j - i)
            i = j

    return merged_chunks


def chunk_documents(documents: List[Document]) -> List[Document]:
    """Takes in a list of documents and chunks them into retrieval-ready chunks with metadata.

    Ensures each chunk has a minimum number of tokens as specified in RAGConfig.MIN_CHUNK_SIZE.
    """
    try:
        config = RAGConfig()
        splitter = _build_text_splitter(config)

        # Show progress while chunking documents
        logger.info(f"Chunking {len(documents)} documents (target size: {config.CHUNK_SIZE} tokens, min: {config.MIN_CHUNK_SIZE} tokens)")
        with tqdm(total=len(documents), desc="Chunking documents", unit="doc") as pbar:
            split_docs = splitter.split_documents(documents)
            pbar.update(len(documents))

        logger.info(f"Initial chunking produced {len(split_docs)} chunks")

        # Merge chunks that are too small
        if config.MIN_CHUNK_SIZE > 0:
            logger.info(f"Merging chunks below {config.MIN_CHUNK_SIZE} tokens...")
            split_docs = _merge_small_chunks(split_docs, config.MIN_CHUNK_SIZE)
            logger.info(f"After merging small chunks: {len(split_docs)} chunks")

        # Verify minimum chunk size
        small_chunks = []
        for i, doc in enumerate(split_docs):
            tokens = _count_tokens(doc.page_content)
            if tokens < config.MIN_CHUNK_SIZE:
                small_chunks.append((i, tokens))

        if small_chunks:
            logger.warning(f"Found {len(small_chunks)} chunks still below minimum size (likely end-of-document chunks)")
            for idx, tokens in small_chunks[:5]:  # Show first 5
                logger.debug(f"Chunk {idx}: {tokens} tokens")
        else:
            logger.info("All chunks meet minimum token requirement")

        return split_docs
    except Exception as e:
        logger.error(f"Error chunking documents: {e}")
        raise e


if __name__ == "__main__":
    documents = load_document(r"C:\Users\User\Projects\hadith_scholar\data\QLORA.pdf")
    chunked_docs = chunk_documents(documents)
    print(chunked_docs)
