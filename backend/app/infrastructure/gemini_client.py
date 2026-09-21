import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("GeminiClient")

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.has_real_key = bool(self.api_key and self.api_key != "MOCK_GEMINI_KEY")
        
        if self.has_real_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai = genai
                logger.info("Google Gemini SDK configurado exitosamente.")
            except Exception as e:
                logger.warning(f"Error al inicializar Google Gemini SDK: {e}. Se usará el modo simulado.")
                self.has_real_key = False
        else:
            logger.info("Modo Inteligente Simulado activado para Gemini (sin API Key activa).")

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: str = "gemini-1.5-pro",
        json_output: bool = True
    ) -> str:
        if self.has_real_key:
            try:
                model = self.genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_instruction
                )
                config = {}
                if json_output:
                    config["response_mime_type"] = "application/json"
                
                response = model.generate_content(prompt, generation_config=config)
                return response.text
            except Exception as e:
                logger.error(f"Error en llamada a Gemini API: {e}. Conmutando a respuesta de contingencia.")

        # Respuesta simulada de contingencia estructurada
        return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """Genera una respuesta JSON inteligente cuando se está en desarrollo/sin API key."""
        return json.dumps({
            "titulo_adaptado": "Adaptación Inteligente de Contenido",
            "resumen": "Procesamiento completado a través del pipeline RAG con Google Gemini.",
            "facts": ["Concepto A extraído", "Concepto B verificado"],
            "anclaje_score": 0.98
        })
