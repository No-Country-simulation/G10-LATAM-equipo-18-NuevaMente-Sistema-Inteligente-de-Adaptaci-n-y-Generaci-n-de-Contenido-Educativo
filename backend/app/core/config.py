"""
config.py

Purpose:
    Application settings and global constants for NuevaMente backend.
    Loads environment variables and defines domain profiles, formats,
    model identifiers, and ingestion limits.

Input:
    Environment variables (e.g. GEMINI_API_KEY, OCI credentials).

Output:
    `settings` instance with typed configuration attributes.
"""

import os
from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "NuevaMente - API de Adaptación Educativa"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Google Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "MOCK_GEMINI_KEY")
    DEFAULT_GEMINI_MODEL_PRO: str = "gemini-1.5-pro"
    DEFAULT_GEMINI_MODEL_FLASH: str = "gemini-1.5-flash"
    DEFAULT_EMBEDDING_MODEL: str = "models/text-embedding-004"

    # OCI Object Storage Configuration (Always Free)
    OCI_CONFIG_FILE: str = os.path.expanduser("~/.oci/config")
    OCI_BUCKET_DOCS: str = "nuevamente-documentos-fuente"
    OCI_BUCKET_ARTIFACTS: str = "nuevamente-contenidos-educativos"

    # RAG Configuration
    MAX_TOP_K_CHUNKS: int = 5
    RRF_DENSE_WEIGHT: float = 0.6
    RRF_SPARSE_WEIGHT: float = 0.4

    # Ingestion Configuration
    SUPPORTED_EXTENSIONS: List[str] = [".pdf", ".md", ".markdown", ".txt"]
    MAX_FILE_SIZE_MB: int = 20
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    CHILD_CHUNK_SIZE: int = 150

    # Domain Profiles
    PROFILE_BEGINNER: str = "beginner"
    PROFILE_JUNIOR_DEV: str = "junior_developer"
    PROFILE_TECH_LEAD: str = "tech_lead"
    PROFILE_EXECUTIVE: str = "executive"

    @property
    def PROFILES(self) -> List[str]:
        return [
            self.PROFILE_BEGINNER,
            self.PROFILE_JUNIOR_DEV,
            self.PROFILE_TECH_LEAD,
            self.PROFILE_EXECUTIVE,
        ]

    # Domain Output Formats
    FORMAT_TUTORIAL: str = "tutorial"
    FORMAT_FLASHCARDS: str = "flashcards"
    FORMAT_QUIZ: str = "quiz"
    FORMAT_SUMMARY: str = "executive_summary"
    FORMAT_CLASS_SCRIPT: str = "class_script"

    @property
    def OUTPUT_FORMATS(self) -> List[str]:
        return [
            self.FORMAT_TUTORIAL,
            self.FORMAT_FLASHCARDS,
            self.FORMAT_QUIZ,
            self.FORMAT_SUMMARY,
            self.FORMAT_CLASS_SCRIPT,
        ]

    # Domain Niches
    NICHE_GENERAL: str = "general"
    NICHE_FINTECH: str = "fintech"
    NICHE_HEALTH: str = "health"
    NICHE_ECOMMERCE: str = "ecommerce"

    @property
    def NICHES(self) -> List[str]:
        return [
            self.NICHE_GENERAL,
            self.NICHE_FINTECH,
            self.NICHE_HEALTH,
            self.NICHE_ECOMMERCE,
        ]


settings = Settings()
