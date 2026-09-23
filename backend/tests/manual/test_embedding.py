"""
test_embedding.py

Prueba manual del EmbeddingService.
Ejecutar desde backend/: uv run python tests/manual/test_embedding.py

Requiere GEMINI_API_KEY en backend/.env para la prueba de API.
Si no está disponible, reporta el error sin fallar todo el script.
"""

import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.embedding_service import EmbeddingService
from app.core.config import settings

SEPARATOR = "-" * 60

SAMPLE_TEXTS = [
    "Las redes neuronales convolucionales son fundamentales en visión computacional.",
    "El modelo aprende representaciones jerárquicas de las características de la imagen.",
    "Fintech refers to technology-driven financial services and innovation.",
]

SAMPLE_QUERY = "¿Cómo funcionan las redes convolucionales?"


def print_vector_preview(label: str, vector: list, n: int = 5) -> None:
    preview = [round(v, 6) for v in vector[:n]]
    print(f"  {label}: dim={len(vector)} | primeros {n} valores: {preview}")


def test_gemini_api():
    print("\n" + SEPARATOR)
    print("PRUEBA 1 — Gemini API (método: api, proveedor: gemini)")
    print(SEPARATOR)
    try:
        svc = EmbeddingService(method="api", provider="gemini")
        print(f"  Modelo activo : {svc.model_name}")

        # Single document embedding
        vec = svc.embed_text(SAMPLE_TEXTS[0], is_query=False)
        print_vector_preview("doc embedding", vec)

        # Query embedding
        q_vec = svc.embed_text(SAMPLE_QUERY, is_query=True)
        print_vector_preview("query embedding", q_vec)

        # Batch embedding
        batch = svc.embed_batch(SAMPLE_TEXTS)
        print(f"  Batch: {len(batch)} vectores, dim={len(batch[0])}")
        print("  ✅ Gemini API OK")
    except Exception as e:
        print(f"  ⚠️  Gemini API no disponible: {e}")


def test_jina_api():
    print("\n" + SEPARATOR)
    print("PRUEBA 2 — Jina AI API (método: api, proveedor: jina)")
    print(SEPARATOR)
    if not settings.JINA_API_KEY:
        print("  ⏭️  JINA_API_KEY no configurada — omitiendo prueba")
        return
    try:
        svc = EmbeddingService(method="api", provider="jina")
        print(f"  Modelo activo : {svc.model_name}")
        vec = svc.embed_text(SAMPLE_TEXTS[0])
        print_vector_preview("doc embedding", vec)
        print("  ✅ Jina API OK")
    except Exception as e:
        print(f"  ⚠️  Jina API no disponible: {e}")


def test_model_name_tracking():
    print("\n" + SEPARATOR)
    print("PRUEBA 3 — Verificación de model_name tracking")
    print(SEPARATOR)
    svc_gemini = EmbeddingService(method="api", provider="gemini")
    svc_jina = EmbeddingService(method="api", provider="jina")
    print(f"  gemini model_name : {svc_gemini.model_name}")
    print(f"  jina   model_name : {svc_jina.model_name}")

    # Simulates what the vector store will check before accepting a query.
    collection_model = svc_gemini.model_name
    query_model = svc_jina.model_name
    compatible = collection_model == query_model
    print(f"  Compatibilidad gemini↔jina : {compatible} (esperado: False)")
    assert not compatible, "Modelos distintos no deben ser compatibles"
    print("  ✅ Tracking de modelo OK")


if __name__ == "__main__":
    print("=" * 60)
    print("NuevaMente — Test Manual: EmbeddingService")
    print(f"Método configurado  : {settings.EMBEDDING_METHOD}")
    print(f"Proveedor por defecto: {settings.EMBEDDING_API_PROVIDER}")
    print("=" * 60)

    test_gemini_api()
    test_jina_api()
    test_model_name_tracking()

    print("\n" + "=" * 60)
    print("Tests completados.")
    print("=" * 60)
