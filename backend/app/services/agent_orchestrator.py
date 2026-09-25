"""
agent_orchestrator.py

Purpose:
    Coordinates multi-agent pipeline using Gemini models to generate
    adapted educational material according to Bloom's taxonomy and profile.
    Loads prompt templates from app/prompts and stores output in OCI storage.

Input:
    AdaptationRequest, retrieved top passages, key concepts, and prerequisites.

Output:
    AdaptationResponse with structured content, evaluation metrics, and storage metadata.
"""

import math
from typing import Dict, Any, List

from app.infrastructure.gemini_client import GeminiClient
from app.infrastructure.groq_client import GroqClient
from app.services.multi_agent_router import MultiAgentRouter
from app.schemas.adaptation import (
    AdaptationRequest,
    AdaptationResponse,
    ResponseMetadata,
    AdaptedContent,
    FlashcardItem,
    QuizItem,
    QualityEvaluation,
    OCIStorageResult,
)
from app.services.oci_storage_service import OCIStorageService
from app.prompts.prompt_loader import load_prompt


class AgentOrchestrator:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.groq_client = GroqClient()
        self.router = MultiAgentRouter()
        self.oci_service = OCIStorageService()

    def run_pipeline(
        self,
        request: AdaptationRequest,
        top_passages: List[Dict[str, Any]],
        key_concepts: List[str],
        prerequisites: List[str],
    ) -> AdaptationResponse:
        """Executes multi-agent pipeline using a Single-Shot Mega Prompt with Gemini 1.5."""
        
        # 1. Armar el Mega-Prompt
        context_text = "\n\n".join([f"Fragmento {i+1}:\n{p.get('content', '')}" for i, p in enumerate(top_passages)])
        
        system_instruction = (
            "Eres un experto diseñador instruccional. Tu tarea es adaptar contenido educativo. "
            "DEBES RESPONDER ÚNICAMENTE CON UN JSON VÁLIDO. "
        )

        prompt = f"""
        Adapta la siguiente información para un estudiante con perfil: '{request.recipient_profile}'
        Formato de salida requerido: '{request.output_format}' (Por ejemplo: Tutorial, Flashcards, Quiz)
        Tema/Nicho: '{request.title}' / '{request.niche}'

        Conceptos clave (generados previamente): {key_concepts}
        Prerrequisitos sugeridos: {prerequisites}
        
        TEXTOS DE CONTEXTO (Usa estrictamente esta información para no alucinar):
        {context_text}
        
        INSTRUCCIONES DE FORMATO JSON:
        Devuelve un JSON con esta estructura exacta (NO USES MARKDOWN ```json, solo el objeto crudo):
        {{
            "metadatos": {{
                "perfil_aplicado": "{request.recipient_profile}",
                "formato_generado": "{request.output_format}",
                "tiempo_estimado_estudio_minutos": 15,
                "conceptos_clave": {key_concepts},
                "prerrequisitos": {prerequisites}
            }},
            "contenido_adaptado": {{
                "titulo": "Un título atractivo",
                "introduccion_contextualizada": "Introducción adaptada...",
                "resumen_ejecutivo": "resumen o null",
                "items": [{{"frente": "...", "dorso": "...", "pista_didactica": "..."}}],
                "quizzes": [{{"pregunta": "...", "opciones": ["..."], "respuesta_correcta": "...", "justificacion_didactica": "..."}}],
                "secciones_tutorial": [{{"encabezado": "...", "contenido": "..."}}]
            }},
            "evaluacion_calidad": {{
                "anclaje_fuente_score": 0.95,
                "claridad_pedagogica": "Alta",
                "observaciones": "Breve nota sobre las analogías"
            }}
        }}
        Nota importante: Asegúrate de llenar 'items', 'quizzes' o 'secciones_tutorial' dependiendo estrictamente del formato de salida solicitado. Los que no apliquen déjalos en null o array vacío.
        """

        import json
        import math
        
        # Enrutamiento Inteligente
        best_agent = self.router.route_task(
            output_format=request.output_format, 
            task_description=request.title
        )
        print(f"🧠 [Multi-Agent Router] Delegando tarea a: {best_agent} (Formato: {request.output_format})")

        try:
            if best_agent == "GROQ":
                raw_response = self.groq_client.generate_content(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    json_output=True
                )
            else:
                raw_response = self.gemini_client.generate_content(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    model_name="gemini-2.5-flash",
                    json_output=True
                )
            # Limpiar posible markdown si Gemini se equivoca e ignora la orden
            raw_response = raw_response.strip().removeprefix("```json").removesuffix("```").strip()
            parsed_data = json.loads(raw_response)
            
            # Usar las llaves en español que coinciden con los aliases de Pydantic
            metadata = ResponseMetadata(**parsed_data.get("metadatos", parsed_data.get("metadata", {})))
            adapted_content = AdaptedContent(**parsed_data.get("contenido_adaptado", parsed_data.get("adapted_content", {})))
            evaluation = QualityEvaluation(**parsed_data.get("evaluacion_calidad", parsed_data.get("quality_evaluation", {})))
            
        except Exception as e:
            # Fallback en caso de error de parseo o de API
            print(f"Error generando contenido (usando fallback): {e}")
            raw_preview = str(raw_response)[:800] if 'raw_response' in locals() else "No response"
            
            metadata = ResponseMetadata(
                profile_applied=request.recipient_profile,
                format_generated=request.output_format,
                estimated_study_time_minutes=5,
                key_concepts=key_concepts,
                prerequisites=prerequisites,
            )
            adapted_content = AdaptedContent(
                title=f"Dominando {request.title} (Fallback)",
                contextualized_introduction="Generación automática falló, modo fallback activado.",
                tutorial_sections=[{"encabezado": "Error", "contenido": "No se pudo generar el JSON."}]
            )
            evaluation = QualityEvaluation(source_grounding_score=0.0, pedagogical_clarity="Baja", observations=f"Error: {str(e)} | RAW: {raw_preview}")

        # Sanitize object name for OCI upload
        sanitized_title = "".join(c if c.isalnum() else "-" for c in request.title.lower())[:15]
        object_name = (
            f"content-{sanitized_title}-{request.recipient_profile.lower()[:10]}-"
            f"{request.output_format.lower()[:10]}-001.json"
        )

        response_data = {
            "status": "exito",
            "metadatos": metadata.model_dump(by_alias=True),
            "contenido_adaptado": adapted_content.model_dump(by_alias=True),
            "evaluacion_calidad": evaluation.model_dump(by_alias=True),
        }

        # Store in OCI Object Storage Always Free
        oci_info = self.oci_service.upload_json_artifact(
            bucket_name="nuevamente-contenidos-educativos",
            object_name=object_name,
            json_data=response_data,
        )

        oci_storage = OCIStorageResult(
            bucket=oci_info["bucket"],
            object_id=oci_info["objeto_id"],
            upload_status=oci_info["status_upload"],
        )

        return AdaptationResponse(
            status="exito",
            metadata=metadata,
            adapted_content=adapted_content,
            quality_evaluation=evaluation,
            oci_storage=oci_storage,
        )
