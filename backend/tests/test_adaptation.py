import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

def test_auth_login_endpoint():
    payload = {
        "email": "ana.martinez@empresa.com",
        "password": "password123",
        "name": "Ana Martínez"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "exito"
    assert data["user"]["name"] == "Ana Martínez"
    assert data["user"]["isLoggedIn"] is True

def test_auth_register_endpoint():
    payload = {
        "name": "Fernando García",
        "email": "fernando.garcia@empresa.com",
        "password": "securepassword"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "exito"
    assert data["user"]["name"] == "Fernando García"
    assert data["user"]["isLoggedIn"] is True
