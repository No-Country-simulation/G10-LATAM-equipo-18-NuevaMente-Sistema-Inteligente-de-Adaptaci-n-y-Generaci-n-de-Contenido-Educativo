import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
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
    
    class Config:
        case_sensitive = True

settings = Settings()
