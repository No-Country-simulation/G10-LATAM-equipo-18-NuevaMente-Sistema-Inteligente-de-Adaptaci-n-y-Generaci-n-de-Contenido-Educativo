from fastapi import APIRouter, HTTPException, status
from app.schemas.adaptation import AdaptationRequest, AdaptationResponse
from app.services.ingester_service import IngesterService
from app.services.hybrid_rag_service import HybridRAGService
from app.services.graph_rag_service import GraphRAGService
from app.services.agent_orchestrator import AgentOrchestrator

router = APIRouter()

ingester_service = IngesterService()
hybrid_rag_service = HybridRAGService()
graph_rag_service = GraphRAGService()
agent_orchestrator = AgentOrchestrator()

@router.post("/adapt-content", response_model=AdaptationResponse, status_code=status.HTTP_200_OK)
async def adapt_content(request: AdaptationRequest):
    """
    Endpoint principal del Hackathon: Recibe el material técnico y parámetros de personalización,
    lo procesa mediante el pipeline de Graph RAG + RAG Híbrido + Orquestación de Agentes Gemini,
    y retorna el paquete educativo estructurado guardado en OCI Object Storage Always Free.
    """
    try:
        # 1. Ingestión y Segmentación AST
        doc_data = ingester_service.parse_and_chunk_document(
            content=request.documento_contenido,
            title=request.documento_titulo
        )
        
        # 2. Graph RAG (Extracción de Conceptos Clave y Prerrequisitos via DAG)
        _, key_concepts, prerequisites = graph_rag_service.build_concept_dag(request.documento_contenido)
        
        # 3. RAG Híbrido (BM25 + Dense Embeddings + Cross-Encoder Re-ranker)
        top_passages = hybrid_rag_service.retrieve_top_passages(
            query=f"{request.perfil_destinatario} {request.formato_salida} {request.nicho_sector}",
            child_chunks=doc_data["child_chunks"],
            parent_chunks=doc_data["parent_chunks"]
        )
        
        # 4. Orquestación Agéntica con Gemini
        response = agent_orchestrator.run_pipeline(
            request=request,
            top_passages=top_passages,
            key_concepts=key_concepts,
            prerequisites=prerequisites
        )
        
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la adaptación de contenido: {str(e)}"
        )
