from fastapi import FastAPI, UploadFile, Form, File, HTTPException
import uvicorn
import shutil
import os
import uuid
import datetime
import json
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# Append paths to import from local services (Simulating microservice calls for this monolithic translation)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from services.rag_service.extractor import extraer_texto, limpiar_texto, crear_chunks
from services.rag_service.vector_store import VectorRAG
from services.llm_service.generator import generar_contenido_llm, revisar_fidelidad, construir_consulta
from services.storage_service.oci_client import subir_bytes_oci

app = FastAPI(title="NuevaMente API Gateway")
rag = VectorRAG()

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "NuevaMente API Gateway en ejecución",
        "docs": "/docs"
    }

@app.post("/generate")
async def generate_endpoint(
    file: UploadFile = File(...),
    perfil: str = Form(...),
    formato: str = Form(...),
    nicho: str = Form(...),
    nivel: str = Form(...)
):
    try:
        # 1. Guardar archivo temporalmente
        temp_dir = "/tmp/nuevamente_docs"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. RAG Service: Extraer y Chunkear
        texto = limpiar_texto(extraer_texto(file_path))
        chunks = crear_chunks(texto)
        if not chunks:
            raise HTTPException(status_code=400, detail="No fue posible extraer texto del documento.")
        
        rag.indexar(chunks)
        
        info = {
            "archivo": file.filename,
            "caracteres_extraidos": len(texto),
            "chunks_indexados": len(chunks)
        }
        
        # 3. Storage Service: Subir original
        with open(file_path, "rb") as f:
            original_bytes = f.read()
        oci_original = subir_bytes_oci(f"documentos/{file.filename}", original_bytes)
        
        # 4. RAG Service: Buscar relevantes
        consulta = construir_consulta(perfil, formato, nicho, nivel)
        recuperados = rag.buscar(consulta)
        
        # 5. LLM Service: Generar contenido
        resultado = generar_contenido_llm(perfil, formato, nicho, nivel, recuperados)
        
        # 6. LLM Service: Revisar Fidelidad
        revision = revisar_fidelidad(resultado, recuperados)
        resultado["revision_fidelidad"] = revision
        resultado["documento"] = info
        resultado["almacenamiento_oci_original"] = oci_original
        
        # 7. Storage Service: Subir Resultado
        nombre_json = f"resultado_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.json"
        contenido_json = json.dumps(resultado, ensure_ascii=False, indent=2)
        
        oci_resultado = subir_bytes_oci(f"resultados/{nombre_json}", contenido_json.encode("utf-8"))
        resultado["almacenamiento_oci_resultado"] = oci_resultado
        
        # Preparar evidencia para frontend
        resumen_fuentes = "\n\n".join(
            f"Chunk {r['chunk_id']} | similitud {r['score']:.3f}\n{r['texto'][:700]}"
            for r in recuperados
        )
        
        return {
            "status": "success",
            "resultado": resultado,
            "evidencia": resumen_fuentes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
