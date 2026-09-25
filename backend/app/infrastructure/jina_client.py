import requests
import os
import logging
from typing import List

logger = logging.getLogger("JinaClient")

class JinaClient:
    """Cliente nativo para la API de Jina AI (Embeddings)."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("JINA_API_KEY", "")
        self.base_url = "https://api.jina.ai/v1/embeddings"
        
    def embed_batch(self, texts: List[str], model_name: str = "jina-embeddings-v3") -> List[List[float]]:
        if not self.api_key or self.api_key == "your_jina_api_key_here":
            logger.warning("JINA_API_KEY no encontrada o es inválida.")
            raise ValueError("JINA_API_KEY is missing or invalid.")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": model_name, "input": texts}
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        
        # Jina returns results sorted by index.
        return [item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"])]
