"""
test_ingester.py (manual)

Purpose:
    Standalone script to manually verify that IngesterService works
    end to end, independent of the rest of the pipeline.
    Run directly with:
        uv run python tests/manual/test_ingester.py
    or:
        python tests/manual/test_ingester.py
"""

import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Add backend directory to sys.path so app modules can be imported
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.ingester_service import IngesterService

SAMPLE_TXT_FILE = Path(__file__).parent / "sample_docs" / "sample_vcn.txt"
SAMPLE_MD_FILE = Path(__file__).parent / "sample_docs" / "sample_sections.md"

if __name__ == "__main__":
    service = IngesterService()

    print("=" * 60)
    print("1. PROBANDO INGESTA DE ARCHIVO TXT (Heurística de Secciones)")
    print("=" * 60)
    print(f"Cargando: {SAMPLE_TXT_FILE.name}")
    txt_doc = service.process_document(SAMPLE_TXT_FILE)

    print(f"Document ID: {txt_doc.document_id}")
    print(f"Título: {txt_doc.title}")
    print(f"Longitud de texto limpio: {len(txt_doc.raw_text)} caracteres")
    print(f"Total de chunks generados: {len(txt_doc.chunks)}")

    for idx, chunk in enumerate(txt_doc.chunks):
        preview = chunk.text[:80].replace("\n", " ")
        print(f"  [{idx + 1}] Section: '{chunk.section_title}' (Level {chunk.heading_level})")
        print(f"      Texto: {preview}...")

    print("\n" + "=" * 60)
    print("2. PROBANDO INGESTA DE ARCHIVO MARKDOWN (Detección AST #)")
    print("=" * 60)
    print(f"Cargando: {SAMPLE_MD_FILE.name}")
    md_doc = service.process_document(SAMPLE_MD_FILE)

    print(f"Document ID: {md_doc.document_id}")
    print(f"Título: {md_doc.title}")
    print(f"Longitud de texto limpio: {len(md_doc.raw_text)} caracteres")
    print(f"Total de chunks generados: {len(md_doc.chunks)}")

    for idx, chunk in enumerate(md_doc.chunks):
        preview = chunk.text[:80].replace("\n", " ")
        print(f"  [{idx + 1}] Section: '{chunk.section_title}' (Level {chunk.heading_level})")
        print(f"      Texto: {preview}...")

    print("\n" + "=" * 60)
    print("3. VERIFICANDO FORMATO JERÁRQUICO RAG (Parent-Child)")
    print("=" * 60)
    rag_data = md_doc.to_rag_format()
    print(f"Total Parents: {rag_data['total_parents']}")
    print(f"Total Children: {rag_data['total_children']}")
    if rag_data["parent_chunks"]:
        p0 = rag_data["parent_chunks"][0]
        print(f"  Ejemplo Parent[0]: ID={p0['id']} | Breadcrumb={p0['breadcrumb']}")
    if rag_data["child_chunks"]:
        c0 = rag_data["child_chunks"][0]
        print(f"  Ejemplo Child[0]: ID={c0['id']} | ParentID={c0['parent_id']} | Content='{c0['content'][:40]}...'")

    SAMPLE_PDF_FILE = Path(__file__).parent / "sample_docs" / "Nueva Mente.pdf"
    print("\n" + "=" * 60)
    print("4. PROBANDO INGESTA DE ARCHIVO PDF (Extracción y Páginas)")
    print("=" * 60)
    if SAMPLE_PDF_FILE.exists():
        print(f"Cargando: {SAMPLE_PDF_FILE.name}")
        pdf_doc = service.process_document(SAMPLE_PDF_FILE)
        print(f"Document ID: {pdf_doc.document_id}")
        print(f"Título: {pdf_doc.title}")
        print(f"Longitud de texto limpio: {len(pdf_doc.raw_text)} caracteres")
        print(f"Total de chunks generados: {len(pdf_doc.chunks)}")
        for chunk in pdf_doc.chunks[:3]:
            preview = chunk.text[:80].replace("\n", " ")
            print(f"  - Chunk (página={chunk.page_number}): {preview}...")
    else:
        print(f"Omitiendo PDF: coloca 'Nueva Mente.pdf' en {SAMPLE_PDF_FILE.parent} para probarlo.")

    print("\n>>> ¡Prueba manual completada exitosamente! <<<")
