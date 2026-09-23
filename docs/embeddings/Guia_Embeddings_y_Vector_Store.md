# Módulo de Embeddings y Vector Store — NuevaMente

Este documento describe la arquitectura, funcionamiento e instrucciones de uso del módulo de generación de embeddings vectoriales y su compatibilidad con el pipeline de recuperación RAG en NuevaMente.

---

## 1. Explicación para Principiantes: ¿Cómo Funciona?

Cuando el módulo de ingestión divide un documento en pequeños fragmentos (chunks), estos siguen siendo texto plano. Las computadoras no pueden comparar fácilmente el significado profundo de dos oraciones basándose únicamente en palabras exactas.

Para resolver esto, convertimos el texto en **Embeddings** (vectores numéricos de alta dimensionalidad):

```
[ Texto del Chunk / Consulta ]
               │
               ▼
1. Selección de Proveedor y Modelo
   - API de Google Gemini (gemini-embedding-001, dim=3072).
   - API de Jina AI (jina-embeddings-v3, dim=1024).
   - Local: sentence-transformers (MiniLM, dim=384) como fallback.
               │
               ▼
2. Vectorización (Embedding)
   - Transforma texto en una lista de números flotantes (ej. [-0.032, 0.016, ...]).
   - Representa matemáticamente el significado semántico del contenido.
               │
               ▼
3. Control Estricto de Compatibilidad (Model Tracking)
   - Se registra en los metadatos qué modelo generó cada vector.
   - Evita comparar vectores de dimensiones o espacios semánticos incompatibles.
```

### Conceptos Clave
- **Espacio Vectorial:** Cada modelo proyecta el texto en un mapa matemático diferente. Comparar un vector de Gemini (3072 números) con uno de Jina (1024 números) es imposible y corrompe los resultados de búsqueda.
- **Fallback Seguro:** Si la API falla (por red o límites de cuota), el sistema puede derivar a un modelo alternativo, pero registra claramente el cambio para evitar mezclar vectores incompatibles en la misma colección.
- **Task Type (Gemini):** Distingue entre vectorizar un documento (`RETRIEVAL_DOCUMENT`) y vectorizar una consulta del usuario (`RETRIEVAL_QUERY`) para maximizar la precisión de recuperación.

---

## 2. Guía Rápida para Desarrolladores: ¿Cómo Usarlo?

Esta sección explica cómo inicializar y usar el servicio de embeddings en el código.

### Uso Directo en Python

```python
from app.services.embedding_service import EmbeddingService

# 1. Inicialización según variables de entorno (por defecto: API Gemini)
embedding_svc = EmbeddingService()

print(f"Método activo: {embedding_svc.method}")      # 'api' o 'local'
print(f"Proveedor: {embedding_svc.provider}")        # 'gemini' o 'jina'
print(f"Modelo activo: {embedding_svc.model_name}")   # 'models/gemini-embedding-001'

# 2. Vectorizar un documento
doc_text = "Una Virtual Cloud Network (VCN) es una red virtual privada en OCI."
vector_doc = embedding_svc.embed_text(doc_text, is_query=False)
print(f"Dimensión del vector: {len(vector_doc)}")

# 3. Vectorizar una consulta de búsqueda
query_text = "¿Qué es una VCN?"
vector_query = embedding_svc.embed_text(query_text, is_query=True)

# 4. Vectorización por lote (Batch)
textos = [
    "Las subredes dividen la red en segmentos públicos y privados.",
    "Las listas de seguridad funcionan como firewalls virtuales."
]
vectores_batch = embedding_svc.embed_batch(textos)
print(f"Vectores generados: {len(vectores_batch)}")
```

### Inicialización con Proveedor Específico
Puedes forzar un proveedor o método al instanciar el servicio:

```python
# Usar Jina AI
jina_svc = EmbeddingService(method="api", provider="jina")

# Usar modelo local (sentence-transformers)
local_svc = EmbeddingService(method="local")
```

---

## 3. Configuración del Entorno (`.env`)

En `backend/.env` se configuran los proveedores y modelos:

```dotenv
# API Keys
GEMINI_API_KEY=AIzaSy...
JINA_API_KEY=jina_...

# Método: 'api' o 'local'
EMBEDDING_METHOD=api

# Proveedor API: 'gemini' o 'jina'
EMBEDDING_API_PROVIDER=gemini

# Vector Store local
VECTOR_STORE_METHOD=chroma
VECTOR_STORE_DIR=vector_store
```

---

## 4. Pruebas Manuales con `uv`

Para validar la conexión con las APIs de embeddings y verificar el control de compatibilidad entre modelos:

```powershell
cd backend
uv run python tests/manual/test_embedding.py
```

El script ejecutará tres comprobaciones:
1. Generación de vector individual, de consulta y batch vía Google Gemini.
2. Generación de vector vía Jina AI (si `JINA_API_KEY` está configurada).
3. Verificación de rechazo de compatibilidad cruzada entre modelos de diferente dimensión.
