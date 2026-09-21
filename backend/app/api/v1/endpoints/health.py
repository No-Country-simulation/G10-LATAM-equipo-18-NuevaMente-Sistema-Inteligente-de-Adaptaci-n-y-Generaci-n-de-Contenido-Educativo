from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "NuevaMente API Engine",
        "version": "1.0.0",
        "oci_always_free": "activo",
        "gemini_pipeline": "listo"
    }
