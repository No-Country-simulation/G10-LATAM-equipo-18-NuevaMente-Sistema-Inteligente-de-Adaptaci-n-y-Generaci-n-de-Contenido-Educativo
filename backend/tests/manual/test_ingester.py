"""
test_ingester.py (manual)

Propósito:
    Script independiente para verificar manualmente que IngesterService
    funciona de punta a punta, sin depender del resto del pipeline.
    Se ejecuta directo con:
        uv run python tests/manual/test_ingester.py
    o:
        python tests/manual/test_ingester.py
"""

import sys
from pathlib import Path

# Asegura salida en UTF-8 en consola de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Agrega la carpeta backend/ al sys.path para poder importar los módulos de app
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.ingester_service import IngesterService

# ---------------------------------------------------------------------------
# Rutas de los archivos de prueba (todas juntas, en un solo lugar)
# ---------------------------------------------------------------------------
SAMPLE_DOCS_DIR = Path(__file__).parent / "sample_docs"
SAMPLE_TXT_FILE = SAMPLE_DOCS_DIR / "sample_vcn.txt"
SAMPLE_MD_FILE = SAMPLE_DOCS_DIR / "sample_sections.md"
SAMPLE_PDF_FILE = SAMPLE_DOCS_DIR / "Nueva Mente.pdf"


def print_document_summary(doc, max_chunks: int = 5):
    """Imprime un resumen legible de un IngestedDocument ya procesado.
    Solo muestra el detalle de los primeros `max_chunks` chunks."""
    print(f"Document ID: {doc.document_id}")
    print(f"Título: {doc.title}")
    print(f"Longitud de texto limpio: {len(doc.raw_text)} caracteres")
    print(f"Total de chunks generados: {len(doc.chunks)}")

    for idx, chunk in enumerate(doc.chunks[:max_chunks]):
        preview = chunk.text[:80].replace("\n", " ")
        print(f"  [{idx + 1}] Sección: '{chunk.section_title}' (Nivel {chunk.heading_level}, Página {chunk.page_number})")
        print(f"      Texto: {preview}...")

    remaining = len(doc.chunks) - max_chunks
    if remaining > 0:
        print(f"  ... y {remaining} chunk(s) más (omitidos para no saturar la consola)")


if __name__ == "__main__":
    service = IngesterService()

    print("=" * 60)
    print("1. PROBANDO INGESTA DE ARCHIVO TXT (Heurística de Secciones)")
    print("=" * 60)
    print(f"Cargando: {SAMPLE_TXT_FILE.name}")
    txt_doc = service.process_document(SAMPLE_TXT_FILE)
    print_document_summary(txt_doc)

    print("\n" + "=" * 60)
    print("2. PROBANDO INGESTA DE ARCHIVO MARKDOWN (Detección de encabezados #)")
    print("=" * 60)
    print(f"Cargando: {SAMPLE_MD_FILE.name}")
    md_doc = service.process_document(SAMPLE_MD_FILE)
    print_document_summary(md_doc)

    print("\n" + "=" * 60)
    print("3. VERIFICANDO FORMATO JERÁRQUICO RAG (Parent-Child)")
    print("=" * 60)
    rag_data = service.build_rag_chunks(md_doc)
    print(f"Total Parents: {rag_data['total_parents']}")
    print(f"Total Children: {rag_data['total_children']}")
    if rag_data["parent_chunks"]:
        p0 = rag_data["parent_chunks"][0]
        print(f"  Ejemplo Parent[0]: ID={p0['id']} | Breadcrumb={p0['breadcrumb']}")
    if rag_data["child_chunks"]:
        c0 = rag_data["child_chunks"][0]
        print(f"  Ejemplo Child[0]: ID={c0['id']} | ParentID={c0['parent_id']} | Content='{c0['content'][:40]}...'")

    print("\n" + "=" * 60)
    print("4. PROBANDO INGESTA DE ARCHIVO PDF (Extracción y Páginas)")
    print("=" * 60)
    if SAMPLE_PDF_FILE.exists():
        print(f"Cargando: {SAMPLE_PDF_FILE.name}")
        pdf_doc = service.process_document(SAMPLE_PDF_FILE)
        print_document_summary(pdf_doc)
    else:
        print(f"Omitiendo PDF: coloca '{SAMPLE_PDF_FILE.name}' en {SAMPLE_PDF_FILE.parent} para probarlo.")

    print("\n>>> ¡Prueba manual completada exitosamente! <<<")