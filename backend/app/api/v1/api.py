from fastapi import APIRouter
from app.api.v1.endpoints import adaptation, ingestion, health

api_router = APIRouter()
api_router.include_router(adaptation.router, tags=["Adaptación Educativa"])
api_router.include_router(ingestion.router, tags=["Ingestión de Documentos"])
api_router.include_router(health.router, tags=["Estado del Sistema"])

