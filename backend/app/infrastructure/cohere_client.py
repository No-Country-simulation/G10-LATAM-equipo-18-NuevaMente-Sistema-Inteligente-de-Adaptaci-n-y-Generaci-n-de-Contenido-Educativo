import os
import logging
from typing import Optional

logger = logging.getLogger("CohereClient")

class CohereClient:
    """Cliente nativo para la API de Cohere (Reranking)."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("COHERE_API_KEY", "")
        self.client = None
        
        if not self.api_key or self.api_key == "pega_tu_llave_de_cohere_aqui" or self.api_key == "your_cohere_api_key_here":
            logger.warning("COHERE_API_KEY no encontrada. El reordenamiento será desactivado.")
        else:
            try:
                import cohere # noqa: PLC0415
                self.client = cohere.ClientV2(self.api_key)
            except Exception as e:
                logger.error(f"Fallo al inicializar Cohere SDK: {e}")
                self.client = None

    def rerank(self, query: str, documents: list, top_n: int = 5, model: str = "rerank-multilingual-v3.0"):
        """
        Reordena documentos usando Cohere V2 Rerank.
        `documents` debe ser una lista de strings o diccionarios con el texto.
        """
        if not self.client:
            raise ValueError("Cohere client no está configurado (Falta API Key).")
            
        return self.client.rerank(
            model=model,
            query=query,
            documents=documents,
            top_n=top_n
        )
