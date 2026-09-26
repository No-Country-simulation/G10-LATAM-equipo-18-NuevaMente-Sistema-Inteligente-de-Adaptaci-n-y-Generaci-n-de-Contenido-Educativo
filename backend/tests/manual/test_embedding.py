"""
test_embedding.py

Prueba manual del EmbeddingService.
Ejecutar desde backend/: uv run python tests/manual/test_embedding.py

Requiere GEMINI_API_KEY en backend/.env para la prueba de API.
Si no está disponible, reporta el error sin fallar todo el script.
"""

import sys
import os
from unittest.mock import patch

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
        print(f"  Model ID (API)   : {svc.model_id}")
        print(f"  Model tag (store): {svc.model_name}")

        # Single document embedding
        vec = svc.embed_text(SAMPLE_TEXTS[0], is_query=False)
        print_vector_preview("doc embedding", vec)
        assert len(vec) == settings.EMBEDDING_DIMENSIONS, (
            f"Se esperaban {settings.EMBEDDING_DIMENSIONS} dimensiones, llegaron {len(vec)}"
        )

        # Query embedding
        q_vec = svc.embed_text(SAMPLE_QUERY, is_query=True)
        print_vector_preview("query embedding", q_vec)

        # Batch embedding
        batch = svc.embed_batch(SAMPLE_TEXTS)
        print(f"  Batch: {len(batch)} vectores, dim={len(batch[0])}")
        print(f"  ✅ Gemini API OK — dimensión fija en {settings.EMBEDDING_DIMENSIONS}")
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
        print(f"  Model ID (API)   : {svc.model_id}")
        print(f"  Model tag (store): {svc.model_name}")
        vec = svc.embed_text(SAMPLE_TEXTS[0])
        print_vector_preview("doc embedding", vec)
        assert len(vec) == settings.EMBEDDING_DIMENSIONS, (
            f"Se esperaban {settings.EMBEDDING_DIMENSIONS} dimensiones, llegaron {len(vec)}"
        )
        print(f"  ✅ Jina API OK — dimensión fija en {settings.EMBEDDING_DIMENSIONS}")
    except Exception as e:
        print(f"  ⚠️  Jina API no disponible: {e}")


def test_model_name_tracking():
    print("\n" + SEPARATOR)
    print("PRUEBA 3 — Verificación de model_name tracking (incluye dimensión)")
    print(SEPARATOR)
    svc_gemini = EmbeddingService(method="api", provider="gemini")
    svc_jina = EmbeddingService(method="api", provider="jina")
    print(f"  gemini model_name : {svc_gemini.model_name}")
    print(f"  jina   model_name : {svc_jina.model_name}")

    dim_suffix = f"@{settings.EMBEDDING_DIMENSIONS}"
    assert svc_gemini.model_name.endswith(dim_suffix), "El tag de Gemini debe incluir la dimensión"
    assert svc_jina.model_name.endswith(dim_suffix), "El tag de Jina debe incluir la dimensión"
    print(f"  Ambos tags incluyen el sufijo de dimensión ({dim_suffix})")

    # Simulates what the vector store will check before accepting a query.
    compatible = svc_gemini.model_name == svc_jina.model_name
    print(f"  Compatibilidad gemini↔jina : {compatible} (esperado: False)")
    assert not compatible, "Modelos distintos no deben ser compatibles"
    print("  ✅ Tracking de modelo OK")


def test_jina_batch_halving_on_failure():
    print("\n" + SEPARATOR)
    print("PRUEBA 4 — Reducción de lote ante fallo (mock, sin red real)")
    print(SEPARATOR)
    print("  Simula que el primer intento de lote de Jina falla y verifica")
    print("  que el servicio reduce el tamaño de lote a la mitad y reintenta,")
    print("  en vez de cambiar de proveedor o truncar el texto.")

    svc = EmbeddingService(method="api", provider="jina")
    texts = [f"fragmento de prueba número {i}" for i in range(4)]
    call_sizes = []

    original_embed_batch = svc._jina_client.embed_batch

    def flaky_embed_batch(piece, **kwargs):
        call_sizes.append(len(piece))
        if len(piece) > 2:
            raise RuntimeError("Fallo simulado: lote demasiado grande")
        # Devuelve vectores dummy del tamaño configurado, sin llamar a la red real.
        return [[0.0] * settings.EMBEDDING_DIMENSIONS for _ in piece]

    with patch.object(svc._jina_client, "embed_batch", side_effect=flaky_embed_batch):
        vectors = svc._embed_jina_in_batches(texts, is_query=False)

    print(f"  Tamaños de lote intentados en orden: {call_sizes}")
    assert len(vectors) == len(texts), "Deben regresar tantos vectores como textos de entrada"
    assert max(call_sizes) > 2 and min(call_sizes) <= 2, (
        "Se esperaba ver un intento grande fallido seguido de uno más chico exitoso"
    )
    print("  ✅ Reducción automática de lote OK — no hubo cambio de proveedor")


if __name__ == "__main__":
    print("=" * 60)
    print("NuevaMente — Test Manual: EmbeddingService")
    print(f"Método configurado   : {settings.EMBEDDING_METHOD}")
    print(f"Proveedor por defecto: {settings.EMBEDDING_API_PROVIDER}")
    print(f"Dimensión configurada: {settings.EMBEDDING_DIMENSIONS}")
    print("=" * 60)

    test_gemini_api()
    test_jina_api()
    test_model_name_tracking()
    test_jina_batch_halving_on_failure()

    print("\n" + "=" * 60)
    print("Tests completados.")
    print("=" * 60)