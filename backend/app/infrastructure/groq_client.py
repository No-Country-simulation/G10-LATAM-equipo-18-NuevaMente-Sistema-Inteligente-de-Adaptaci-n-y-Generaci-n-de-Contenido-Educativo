import json
import logging
import os
from typing import Optional

logger = logging.getLogger("GroqClient")

class GroqClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.has_real_key = bool(self.api_key and self.api_key != "your_groq_api_key_here")
        self._client = None

        if self.has_real_key:
            try:
                from groq import Groq  # noqa: PLC0415
                self._client = Groq(api_key=self.api_key)
                logger.info("Groq SDK configured successfully.")
            except Exception as exc:
                logger.warning("Failed to initialize Groq SDK: %s. Using mock mode.", exc)
                self.has_real_key = False
        else:
            logger.info("Groq mock mode active (no valid API key).")

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: str = "llama3-70b-8192",
        json_output: bool = True,
    ) -> str:
        """
        Generates content using Groq. Falls back to mock on any error.
        """
        if self.has_real_key and self._client is not None:
            try:
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                response = self._client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    response_format={"type": "json_object"} if json_output else {"type": "text"}
                )
                return response.choices[0].message.content
            except Exception as exc:
                logger.error("Groq API call failed: %s. Switching to mock response.", exc)

        return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """Returns a structured JSON string for development / no-key environments."""
        return json.dumps({
            "metadatos": {
                "perfil_aplicado": "Estudiante (Mock Groq)",
                "formato_generado": "Fast Generation",
                "tiempo_estimado_estudio_minutos": 5,
                "conceptos_clave": ["Groq", "Velocidad"],
                "prerrequisitos": []
            },
            "contenido_adaptado": {
                "titulo": "Generación Rápida con Groq (Mock)",
                "introduccion_contextualizada": "Groq LPU no tiene llave o falló.",
                "resumen_ejecutivo": "Pipeline de baja latencia simulado.",
                "items": [],
                "quizzes": [],
                "secciones_tutorial": []
            },
            "evaluacion_calidad": {
                "anclaje_fuente_score": 1.0,
                "claridad_pedagogica": "Alta",
                "observaciones": "Respuesta desde Groq simulado."
            }
        })
