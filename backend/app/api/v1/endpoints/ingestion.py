"""
ingestion.py

Purpose:
    FastAPI router handling document upload, validation, parsing,
    and structured layout-aware chunking for PDF, Markdown, and TXT files.

Input:
    Uploaded file (multipart/form-data) via HTTP POST.

Output:
    JSON response containing cleaned text, suggested title, chunks, and metadata.
"""

import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from app.core.config import settings
from app.services.ingester_service import IngesterService

router = APIRouter()
ingester_service = IngesterService()


@router.post("/parse-document", status_code=status.HTTP_200_OK)
@router.post("/parse-pdf", status_code=status.HTTP_200_OK)
async def parse_document(file: UploadFile = File(...)):
    """
    Receives a technical document (PDF, Markdown, or TXT), validates size
    and format, extracts clean content, and returns structured metadata
    with Spanish keys for UI presentation.
    """
    filename = file.filename or "document.txt"
    extension = Path(filename).suffix.lower()

    # Validate file extension
    if extension not in settings.SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no compatible: {extension}. Formatos soportados: {settings.SUPPORTED_EXTENSIONS}",
        )

    try:
        content_bytes = await file.read()

        # Validate file size
        size_mb = len(content_bytes) / (1024 * 1024)
        if size_mb > settings.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Archivo demasiado pesado: {size_mb:.1f}MB. El límite permitido es de {settings.MAX_FILE_SIZE_MB}MB.",
            )

        # Write temporarily to disk for path-based extraction
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
            temp_file.write(content_bytes)
            temp_path = Path(temp_file.name)

        try:
            suggested_title = Path(filename).stem.replace("_", " ").replace("-", " ").title()
            ingested_doc = ingester_service.process_document(temp_path, title=suggested_title)
        finally:
            if temp_path.exists():
                temp_path.unlink()

        return {
            "status": "exito",
            "filename": filename,
            "titulo_sugerido": ingested_doc.title,
            "total_chunks": len(ingested_doc.chunks),
            "texto_extraido": ingested_doc.raw_text,
            "chunks": [chunk.model_dump() for chunk in ingested_doc.chunks],
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el procesamiento del documento: {str(error)}",
        )
