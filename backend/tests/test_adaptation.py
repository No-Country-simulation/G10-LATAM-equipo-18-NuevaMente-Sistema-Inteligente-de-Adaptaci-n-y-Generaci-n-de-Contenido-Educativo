from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_adapt_content_endpoint():
    payload = {
        "documento_titulo": "Introduccion a la Arquitectura de Redes VCN en OCI",
        "documento_contenido": "La Virtual Cloud Network (VCN) es una red privada y personalizable configurada en Oracle Cloud Infrastructure.",
        "perfil_destinatario": "Principiante",
        "formato_salida": "Flashcards",
        "nicho_sector": "General",
        "nivel_detalle": "Didactico"
    }
    
    response = client.post("/api/v1/adapt-content", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "exito"
    assert "metadatos" in data
    assert "contenido_adaptado" in data
    assert "evaluacion_calidad" in data
    assert "almacenamiento_oci" in data
    assert data["evaluacion_calidad"]["anclaje_fuente_score"] >= 0.90
