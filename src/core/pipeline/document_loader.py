"""PDF document loading using the langchain-community PyPDF loader."""

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from logging import getLogger

logger = getLogger(__name__)


def load_document(
    file_path: str | Path, *, max_pages: int | None = None
) -> List[Document]:
    """Load a PDF using langchain-community's PyPDF loader and optional page limit.

    Args:
        file_path: Path to the PDF file.
        max_pages: Optional limit on the number of pages to return starting from
            the first page.

    Returns:
        List of LangChain ``Document`` objects produced by the loader.
    """
    logger.info(f"Loading document from {file_path}")
    try:
        loader = PyPDFLoader(str(file_path))
        documents = loader.load()
    except Exception as e:
        logger.error(f"Error loading document: {e}")
        raise e
    try:
        if max_pages is not None:
            if max_pages <= 0:
                raise ValueError("max_pages must be positive when provided")
            documents = documents[:max_pages]
    except Exception as e:
        logger.error(f"Error applying max_pages: {e}")
        raise e
    logger.info(f"Document loaded successfully from {file_path}")
    return documents




def save_documents(documents: List[Document], output_file: str) -> Path:
    """Write the text content of each Document to a plain text file."""
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for doc in documents:
                f.write(doc.page_content + "\n")
        return Path(output_file)
    except Exception as e:
        logger.error(f"Error saving documents: {e}")
        raise e


if __name__ == "__main__":
    test_file = Path(r"C:\Users\User\Projects\hadith_scholar\data\QLORA.pdf")
    print(f"Loading document with PyPDFLoader: {test_file}")
    docs = load_document(test_file, max_pages=30)
    save_documents(docs, "data/QLORA.txt")
    print(f"Documents saved to {docs}")
