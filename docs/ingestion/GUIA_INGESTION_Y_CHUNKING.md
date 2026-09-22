# Módulo de Ingestión y Chunking — NuevaMente

Este documento describe la arquitectura, funcionamiento e instrucciones de uso del módulo de carga, limpieza y segmentación de documentos técnicos en NuevaMente.

---

## 1. Explicación para Principiantes: ¿Cómo Funciona?

Cuando un usuario sube un archivo (manual técnico, documentación o guía) al sistema, el texto no se puede enviar directamente a un modelo de lenguaje porque suele ser demasiado largo, tener contenido basura (como números de página o cabeceras repetitivas) y carecer de estructura clara.

El módulo de ingestión realiza **3 pasos esenciales**:

```
[ Archivo Crudo ] 
       │ (.pdf, .md, .txt)
       ▼
1. Validación y Extracción
   - Verifica extensión permitida y límite de tamaño (máx. 20MB).
   - Elimina ruido visual en PDFs (cabeceras y pies de página repetidos).
       │
       ▼
2. Detección de Secciones
   - En Markdown: reconoce encabezados jerárquicos (#, ##, ###).
   - En Texto plano: detecta patrones de capítulos y mayúsculas.
   - En PDF: etiqueta y divide el contenido por número de página.
       │
       ▼
3. Segmentación Inteligente (Chunking)
   - Corta el texto respetando párrafos y límites de oraciones (sin cortar palabras a la mitad).
   - Prepara los datos en formato jerárquico Padre-Hijo (Parent-Child) listo para RAG.
```

### Conceptos Clave
- **Sección (Parent Chunk):** Es el bloque temático completo (por ejemplo, todo el apartado *"Configuración de Subredes"*). Aporta todo el contexto educativo al LLM.
- **Fragmento (Child Chunk):** Subdivisión más pequeña dentro de la sección. Sirve para calcular vectores (embeddings) con alta precisión matemática.

---

## 2. Guía Rápida para Desarrolladores: ¿Cómo Usarlo?

Esta sección está pensada para que cualquier miembro del equipo continúe implementando sobre este módulo sin fricción.

### Ingesta Directa en Python
```python
from pathlib import Path
from app.services.ingester_service import IngesterService

# Inicializar servicio
ingester = IngesterService()

# Procesar archivo (.pdf, .md o .txt)
doc = ingester.process_document(Path("ruta/a/mi_documento.pdf"), title="Mi Manual")

# 1. Acceso a los atributos del documento
print(f"ID: {doc.document_id}")
print(f"Título: {doc.title}")
print(f"Total de chunks: {len(doc.chunks)}")

# 2. Conversión automática para el pipeline de RAG (Parent-Child)
rag_payload = doc.to_rag_format()
# Contiene: rag_payload["parent_chunks"] y rag_payload["child_chunks"]
```

### Estructura de los Objetos
- **`doc.chunks`** (`List[DocumentChunk]`):
  - `chunk_id`: Identificador único (ej. `uuid-0`).
  - `text`: Texto limpio del fragmento.
  - `section_title`: Título de la sección de origen (o `None`).
  - `heading_level`: Nivel jerárquico (1 para `#`, 2 para `##`, etc.).
  - `page_number`: Número de página (específico para PDFs).
- **`rag_payload`** (`dict`):
  - `parent_chunks`: Lista con formato `{"id", "title", "breadcrumb", "content", "metadata"}`.
  - `child_chunks`: Lista con formato `{"id", "parent_id", "breadcrumb", "content", "metadata"}`.

### Endpoint HTTP (FastAPI)
- **Ruta:** `POST /api/v1/parse-document` (también compatible con `/api/v1/parse-pdf`)
- **Parámetro:** `file` (multipart/form-data)
- **Formatos aceptados:** `.pdf`, `.md`, `.markdown`, `.txt` (hasta 20 MB).
- **Respuesta (JSON):**
  ```json
  {
    "status": "exito",
    "filename": "manual_oci.pdf",
    "titulo_sugerido": "Manual Oci",
    "total_chunks": 12,
    "texto_extraido": "...",
    "chunks": [ ... ]
  }
  ```

---

## 3. Pruebas Manuales con `uv`

Para verificar el funcionamiento del procesador sin necesidad de levantar el servidor web:

```powershell
cd backend
uv run python tests/manual/test_ingester.py
```
El script procesará los archivos de muestra ubicados en `backend/tests/manual/sample_docs/` e imprimirá la estructura de chunks detectada.
