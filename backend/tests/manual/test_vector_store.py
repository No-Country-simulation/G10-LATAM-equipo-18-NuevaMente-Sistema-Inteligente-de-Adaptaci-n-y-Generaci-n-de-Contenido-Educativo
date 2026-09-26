"""
test_vector_store.py

Prueba manual de la cadena completa:
Ingesta -> Chunking (Parent-Child) -> Embeddings -> Vector Store (FAISS).

Ejecución desde backend/:
uv run python tests/manual/test_vector_store.py
"""

import os
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.embedding_service import EmbeddingService
from app.services.ingester_service import IngesterService
from app.services.vector_store_service import (
    FAISSVectorStore,
    IncompatibleEmbeddingModelError,
)

SEPARATOR = "-" * 60
TEST_INDEX_DIR = Path(__file__).parent / "sample_vector_store"


def cleanup_test_dir():
    if TEST_INDEX_DIR.exists():
        shutil.rmtree(TEST_INDEX_DIR)


def run_full_pipeline_test():
    print("=" * 60)
    print("NuevaMente — Test Manual: FAISS Vector Store Pipeline")
    print("=" * 60)

    cleanup_test_dir()

    # Step 1: Ingestion and Parent-Child chunking
    print("\n" + SEPARATOR)
    print("PASO 1: Ingesta y Fragmentación Jerárquica")
    print(SEPARATOR)
    sample_file = Path(__file__).parent / "sample_docs" / "sample_sections.md"
    ingester = IngesterService()
    document = ingester.process_document(sample_file, title="Documentación OCI Redes")
    rag_payload = ingester.build_rag_chunks(document)

    parent_chunks = rag_payload["parent_chunks"]
    child_chunks = rag_payload["child_chunks"]

    print(f"  Documento procesado : {document.title}")
    print(f"  Parent Chunks creados: {len(parent_chunks)}")
    print(f"  Child Chunks creados : {len(child_chunks)}")
    assert len(parent_chunks) > 0 and len(child_chunks) > 0
    print("  ✅ Ingesta y Chunking OK")

    # Step 2: Embedding Generation
    print("\n" + SEPARATOR)
    print("PASO 2: Generación de Embeddings para Child Chunks")
    print(SEPARATOR)
    embedding_svc = EmbeddingService()
    print(f"  Proveedor activo : {embedding_svc.provider}")
    print(f"  Modelo activo    : {embedding_svc.model_name}")

    child_texts = [c["content"] for c in child_chunks]
    embeddings = embedding_svc.embed_batch(child_texts)

    dim = len(embeddings[0])
    print(f"  Vectores generados: {len(embeddings)} | Dimensión: {dim}")
    print("  ✅ Generación de Embeddings OK")

    # Step 3: Vector Store Indexing
    print("\n" + SEPARATOR)
    print("PASO 3: Indexación en FAISS Vector Store")
    print(SEPARATOR)
    vector_store = FAISSVectorStore(model_name=embedding_svc.model_name)
    vector_store.add_documents(
        child_chunks=child_chunks,
        embeddings=embeddings,
        parent_chunks=parent_chunks,
        model_name=embedding_svc.model_name,
    )
    print(f"  Total vectores en índice FAISS: {vector_store.index.ntotal}")
    assert vector_store.index.ntotal == len(child_chunks)
    print("  ✅ Indexación en FAISS OK")

    # Step 4: Semantic Search & Parent Document Resolution
    print("\n" + SEPARATOR)
    print("PASO 4: Búsqueda Semántica y Resolución de Padres")
    print(SEPARATOR)
    query = "firewall virtual y filtrado de tráfico"
    print(f"  Consulta: '{query}'")

    query_vector = embedding_svc.embed_text(query, is_query=True)

    # 4.1 Search child chunks
    child_results = vector_store.similarity_search(
        query_embedding=query_vector,
        query_model_name=embedding_svc.model_name,
        top_k=2,
    )
    print("  Hijos más relevantes encontrados:")
    for idx, c in enumerate(child_results):
        print(f"    [{idx+1}] Score: {c['score']:.4f} | Parent: {c['parent_id']} | Breadcrumb: {c['breadcrumb']}")

    # 4.2 Retrieve parent documents
    parent_results = vector_store.retrieve_parent_chunks(
        query_embedding=query_vector,
        query_model_name=embedding_svc.model_name,
        top_k_parents=1,
    )
    print("  Padres recuperados para contexto del LLM:")
    for idx, p in enumerate(parent_results):
        print(f"    [{idx+1}] ID: {p['id']} | Título: {p['title']} | Relevance Score: {p['relevance_score']:.4f}")
        print(f"        Contenido: {p['content'][:120]}...")

    assert len(parent_results) > 0
    # Expected best match for firewall query is Security Lists
    assert "Security Lists" in parent_results[0]["title"] or "Security" in parent_results[0]["content"]
    print("  ✅ Búsqueda Semántica y Recuperación de Padres OK")

    # Step 5: Persistence (Save & Load)
    print("\n" + SEPARATOR)
    print("PASO 5: Persistencia (Guardar y Cargar Índice desde Disco)")
    print(SEPARATOR)
    vector_store.save(str(TEST_INDEX_DIR))
    print(f"  Índice guardado en: {TEST_INDEX_DIR}")
    assert (TEST_INDEX_DIR / "index.faiss").exists()
    assert (TEST_INDEX_DIR / "metadata.json").exists()

    loaded_store = FAISSVectorStore()
    loaded_store.load(str(TEST_INDEX_DIR))
    print(f"  Índice cargado con éxito. Total vectores: {loaded_store.index.ntotal}")
    assert loaded_store.index.ntotal == vector_store.index.ntotal

    # Verify search still works on loaded index
    loaded_search = loaded_store.similarity_search(
        query_embedding=query_vector,
        query_model_name=loaded_store.model_name,
        top_k=1,
    )
    print(f"  Búsqueda post-carga score: {loaded_search[0]['score']:.4f}")
    assert len(loaded_search) == 1
    print("  ✅ Persistencia en Disco OK")

    # Step 6: Model Incompatibility Protection
    print("\n" + SEPARATOR)
    print("PASO 6: Protección de Incompatibilidad entre Modelos")
    print(SEPARATOR)
    incompatible_model = "modelo-incompatible-v999"
    try:
        loaded_store.similarity_search(
            query_embedding=query_vector,
            query_model_name=incompatible_model,
        )
        print("  ❌ ERROR: No debió permitir la búsqueda con modelo incompatible.")
        assert False
    except IncompatibleEmbeddingModelError as err:
        print(f"  Capturada excepción esperada: {err}")
        print("  ✅ Bloqueo por modelo incompatible OK")

    cleanup_test_dir()
    print("\n" + "=" * 60)
    print("¡Todos los tests del Vector Store pasaron exitosamente!")
    print("=" * 60)


if __name__ == "__main__":
    run_full_pipeline_test()
