"""
gemini_client.py

Purpose:
    Thin wrapper around the Google Gemini SDK (google-genai v2.x) for
    text generation. Falls back to a structured mock response when no
    valid API key is present (development / CI mode).

Input:
    GEMINI_API_KEY environment variable.
    prompt (str), optional system_instruction (str), model_name (str).

Output:
    Generated text (str), or a JSON mock string in fallback mode.
"""

import json
import logging
import os
from typing import Optional

logger = logging.getLogger("GeminiClient")


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.has_real_key = bool(self.api_key and self.api_key != "MOCK_GEMINI_KEY")
        self._client = None

        if self.has_real_key:
            try:
                # google-genai v2.x — client-based API
                from google import genai  # noqa: PLC0415
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Google Gemini SDK (google-genai v2) configured successfully.")
            except Exception as exc:
                logger.warning("Failed to initialize Gemini SDK: %s. Using mock mode.", exc)
                self.has_real_key = False
        else:
            logger.info("Gemini mock mode active (no valid API key).")

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        json_output: bool = True,
    ) -> str:
        """
        Generates content using Gemini. Falls back to mock on any error.

        Args:
            prompt: User-facing prompt text.
            system_instruction: Optional system role instruction.
            model_name: Gemini model identifier.
            json_output: When True, requests application/json MIME type.
        """
        if self.has_real_key and self._client is not None:
            try:
                from google.genai import types  # noqa: PLC0415

                config_kwargs = {}
                if json_output:
                    config_kwargs["response_mime_type"] = "application/json"
                if system_instruction:
                    config_kwargs["system_instruction"] = system_instruction

                response = self._client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(**config_kwargs) if config_kwargs else None,
                )
                return response.text
            except Exception as exc:
                logger.error("Gemini API call failed: %s. Switching to mock response.", exc)

        return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """Returns a structured JSON string for development / no-key environments."""
        return json.dumps({
            "titulo_adaptado": "Adaptación Inteligente de Contenido",
            "resumen": "Procesamiento completado a través del pipeline RAG con Google Gemini.",
            "facts": ["Concepto A extraído", "Concepto B verificado"],
            "anclaje_score": 0.98,
        })
