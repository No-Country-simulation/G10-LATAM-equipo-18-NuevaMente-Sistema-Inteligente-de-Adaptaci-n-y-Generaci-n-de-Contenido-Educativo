"""
test_ingester.py (manual)

Propósito:
    Script independiente para verificar manualmente que IngesterService
    funciona de punta a punta, evaluando las mejoras implementadas:
    1. Extracción limpia de archivos TXT y Markdown (AST de encabezados).
    2. Conversión estructurada de PDFs:
       - Vía PdfParserService (pymupdf4llm a Markdown) si está disponible.
       - Vía extractor clásico pypdf con limpieza de ruido y metadatos de página como fallback.
    3. Construcción jerárquica RAG (Parent-Child) con metadatos enriquecidos (conceptos clave).
    4. Comparativa de calidad de extracción y segmentación.

Ejecución directo con:
    uv run python tests/manual/test_ingester.py
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
from app.services.pdf_parser_service import PdfParserService

# ---------------------------------------------------------------------------
# Rutas de los archivos de prueba
# ---------------------------------------------------------------------------
SAMPLE_DOCS_DIR = Path(__file__).parent / "sample_docs"
SAMPLE_TXT_FILE = SAMPLE_DOCS_DIR / "sample_vcn.txt"
SAMPLE_MD_FILE = SAMPLE_DOCS_DIR / "sample_sections.md"
SAMPLE_PDF_FILE = SAMPLE_DOCS_DIR / "Nueva Mente.pdf"


def print_document_summary(doc, max_chunks: int = 4):
    """Imprime un resumen legible de un IngestedDocument ya procesado."""
    print(f"Document ID             : {doc.document_id}")
    print(f"Título                  : {doc.title}")
    print(f"Longitud de texto limpio: {len(doc.raw_text)} caracteres")
    print(f"Total de chunks         : {len(doc.chunks)}")

    for idx, chunk in enumerate(doc.chunks[:max_chunks]):
        preview = chunk.text[:90].replace("\n", " ")
        print(f"  [{idx + 1}] Sección: '{chunk.section_title}' (Nivel {chunk.heading_level}, Página {chunk.page_number})")
        print(f"      Texto: {preview}...")

    remaining = len(doc.chunks) - max_chunks
    if remaining > 0:
        print(f"  ... y {remaining} chunk(s) adicionales")


def test_txt_ingestion(service: IngesterService):
    print("=" * 60)
    print("1. PROBANDO INGESTA TXT (Heurística de Secciones)")
    print("=" * 60)
    print(f"Cargando: {SAMPLE_TXT_FILE.name}")
    txt_doc = service.process_document(SAMPLE_TXT_FILE)
    print_document_summary(txt_doc)
    assert len(txt_doc.chunks) > 0, "No se generaron chunks para TXT"
    print("  ✅ Ingesta de TXT OK")


def test_markdown_ingestion(service: IngesterService):
    print("\n" + "=" * 60)
    print("2. PROBANDO INGESTA MARKDOWN (Detección de encabezados #)")
    print("=" * 60)
    print(f"Cargando: {SAMPLE_MD_FILE.name}")
    md_doc = service.process_document(SAMPLE_MD_FILE)
    print_document_summary(md_doc)
    assert len(md_doc.chunks) > 0, "No se generaron chunks para Markdown"
    print("  ✅ Ingesta de Markdown OK")
    return md_doc


def test_parent_child_rag(service: IngesterService, doc):
    print("\n" + "=" * 60)
    print("3. VERIFICANDO FORMATO JERÁRQUICO RAG (Parent-Child + Metadatos)")
    print("=" * 60)
    rag_data = service.build_rag_chunks(doc)
    print(f"Total Parents : {rag_data['total_parents']}")
    print(f"Total Children: {rag_data['total_children']}")

    if rag_data["parent_chunks"]:
        p0 = rag_data["parent_chunks"][0]
        print(f"  Ejemplo Parent[0]: ID={p0['id']} | Breadcrumb={p0['breadcrumb']}")
        key_concepts = p0.get("metadata", {}).get("key_concepts", [])
        if key_concepts:
            print(f"  Conceptos clave detectados en Parent[0]: {key_concepts}")
        else:
            print("  Conceptos clave: [N/A o modo ligero sin KeyBERT]")

    if rag_data["child_chunks"]:
        c0 = rag_data["child_chunks"][0]
        print(f"  Ejemplo Child[0] : ID={c0['id']} | ParentID={c0['parent_id']} | Fragmento='{c0['content'][:50]}...'")

    assert rag_data["total_parents"] > 0 and rag_data["total_children"] > 0
    print("  ✅ Estructura Parent-Child RAG OK")


def test_pdf_ingestion(service: IngesterService):
    print("\n" + "=" * 60)
    print("4. PROBANDO INGESTA Y PARSEO DE ARCHIVOS PDF")
    print("=" * 60)
    if not SAMPLE_PDF_FILE.exists():
        print(f"Omitiendo PDF: coloca '{SAMPLE_PDF_FILE.name}' en {SAMPLE_PDF_FILE.parent} para probarlo.")
        return

    # Comprobación del estado de PdfParserService
    pdf_parser = PdfParserService()
    print(f"Estado de PdfParserService (pymupdf4llm): {'DISPONIBLE (Modo Markdown Avanzado)' if pdf_parser.is_available else 'NO DISPONIBLE (Usando Fallback pypdf)'}")

    print(f"Cargando: {SAMPLE_PDF_FILE.name}")
    pdf_doc = service.process_document(SAMPLE_PDF_FILE)
    print_document_summary(pdf_doc, max_chunks=5)

    # Verificamos si detectó secciones de Markdown o páginas
    sections_detected = sum(1 for c in pdf_doc.chunks if c.section_title is not None)
    pages_detected = sum(1 for c in pdf_doc.chunks if c.page_number is not None)
    print(f"\nResumen de Extracción PDF:")
    print(f"  - Chunks con títulos de sección detectados: {sections_detected}")
    print(f"  - Chunks con información de página: {pages_detected}")
    print("  ✅ Ingesta de PDF OK")


if __name__ == "__main__":
    service = IngesterService()

    test_txt_ingestion(service)
    md_document = test_markdown_ingestion(service)
    test_parent_child_rag(service, md_document)
    test_pdf_ingestion(service)

    print("\n" + "=" * 60)
    print(">>> ¡Prueba manual completada exitosamente! <<<")
    print("=" * 60)