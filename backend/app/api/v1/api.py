from fastapi import APIRouter
from app.api.v1.endpoints import adaptation, health

api_router = APIRouter()
api_router.include_router(adaptation.router, tags=["Adaptación Educativa"])
api_router.include_router(health.router, tags=["Estado del Sistema"])
