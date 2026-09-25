import os
import logging
from typing import Optional

logger = logging.getLogger("PdfParserService")

class PdfParserService:
    """
    Servicio encargado de procesar documentos PDF y convertirlos a Markdown
    limpio y estructurado usando pymupdf4llm. 
    Este Markdown es ideal para ser ingerido por el LLM o dividido en chunks.
    """
    def __init__(self):
        # Intentamos importar para verificar que está instalado
        try:
            import pymupdf4llm  # noqa: F401, PLC0415
            self.is_available = True
        except ImportError:
            logger.error("pymupdf4llm no está instalado. Ejecuta: uv pip install pymupdf4llm")
            self.is_available = False

    def parse_pdf_to_markdown(self, pdf_path: str) -> str:
        """
        Lee un archivo PDF en el disco y lo convierte a formato Markdown.
        Conserva tablas, jerarquías de encabezados y listas.
        """
        if not self.is_available:
            raise RuntimeError("PdfParserService no está disponible por falta de dependencias.")
            
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo PDF no existe en la ruta: {pdf_path}")
            
        import pymupdf4llm  # noqa: PLC0415
        
        logger.info(f"Parseando PDF a Markdown: {pdf_path}")
        try:
            # to_markdown extrae tablas, encabezados y formatea perfecto para RAG
            md_text = pymupdf4llm.to_markdown(pdf_path)
            return md_text
        except Exception as e:
            logger.error(f"Error procesando PDF: {str(e)}")
            raise e
