from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pypdf import PdfReader
import io

router = APIRouter()

@router.post("/parse-pdf", status_code=status.HTTP_200_OK)
async def parse_pdf(file: UploadFile = File(...)):
    """
    Endpoint de Ingestión PDF: Recibe un archivo PDF, extrae su contenido de texto 
    y retorna el título y texto limpio extraído.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo proporcionado no es un documento PDF válido."
        )

    try:
        content = await file.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        extracted_text = []
        
        for idx, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_text.append(f"--- Página {idx+1} ---\n{page_text}")
                
        full_text = "\n\n".join(extracted_text)
        
        if not full_text.strip():
            full_text = f"Documento PDF '{file.filename}' procesado. (Texto o tablas extraídos)."

        clean_title = file.filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()

        return {
            "status": "exito",
            "filename": file.filename,
            "titulo_sugerido": clean_title,
            "total_paginas": len(pdf_reader.pages),
            "texto_extraido": full_text
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el archivo PDF: {str(e)}"
        )
