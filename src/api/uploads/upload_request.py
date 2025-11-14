"""
FastAPI router for file upload and ingestion endpoints.

This module provides endpoints for uploading PDF files and ingesting them
into the vector store for document retrieval.
"""

import os
import tempfile
from logging import getLogger

from fastapi import APIRouter, File, UploadFile, HTTPException

from src.api.schemas.uploads import PresignRequest, PresignResponse, IngestPDFResponse
from src.core.pipeline.ingestion_flow import ingestion_flow

logger = getLogger(__name__)

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])


@router.post("/presign", response_model=PresignResponse)
async def presign(request: PresignRequest, file_upload: UploadFile = File(...)):
    """Generate presigned URL for file upload."""
    return PresignResponse(
        url=request.url, key=request.key, mime=file_upload.content_type
    )


@router.post("/ingest-pdf", response_model=IngestPDFResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    """
    Ingest a PDF file into the vector store.

    Args:
        file: Uploaded PDF file

    Returns:
        IngestPDFResponse with success message and file path

    Raises:
        HTTPException: If file validation fails or ingestion fails
    """
    logger.info(f"Received PDF ingestion request: {file.filename}")

    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    if file.content_type not in ["application/pdf", "application/x-pdf"]:
        logger.warning(f"Unexpected content type: {file.content_type}")

    temp_file_path = None
    try:
        # Create temporary file to store the upload
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
            prefix="upload_"
        ) as temp_file:
            # Read and write file content
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        logger.info(f"Saved uploaded file to: {temp_file_path}")

        # Run ingestion pipeline
        ingestion_flow(temp_file_path)

        logger.info(f"Successfully ingested PDF: {file.filename}")

        return IngestPDFResponse(
            message=f"Successfully ingested {file.filename}",
            file_path=temp_file_path,
            chunks_ingested=0  # Could be enhanced to return actual count
        )

    except ValueError as e:
        logger.error(f"Validation error during ingestion: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.exception(f"Error ingesting PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest PDF: {str(e)}"
        )

    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
