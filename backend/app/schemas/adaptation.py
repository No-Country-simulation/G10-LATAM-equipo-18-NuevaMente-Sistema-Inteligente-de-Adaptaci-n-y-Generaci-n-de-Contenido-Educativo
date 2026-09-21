from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field

class AdaptationRequest(BaseModel):
    documento_titulo: str = Field(..., example="Introduccion a la Arquitectura de Redes VCN en OCI")
    documento_contenido: str = Field(..., example="La Virtual Cloud Network (VCN) es una red privada y personalizable configurada en Oracle Cloud Infrastructure...")
    perfil_destinatario: str = Field(..., example="Principiante")  # Principiante, Desarrollador, Arquitecto, Ejecutivo
    formato_salida: str = Field(..., example="Flashcards")         # Flashcards, Tutorial, Quiz, TLDR
    nicho_sector: str = Field(default="General", example="General") # Fintech, Salud, E-commerce, General
    nivel_detalle: str = Field(default="Didactico", example="Didactico")

class FlashcardItem(BaseModel):
    frente: str
    dorso: str
    pista_didactica: Optional[str] = None

class QuizItem(BaseModel):
    pregunta: str
    opciones: List[str]
    respuesta_correcta: str
    justificacion_didactica: str

class ContenidoAdaptado(BaseModel):
    titulo: str
    introduccion_contextualizada: str
    resumen_ejecutivo: Optional[str] = None
    items: Optional[List[FlashcardItem]] = None
    quizzes: Optional[List[QuizItem]] = None
    secciones_tutorial: Optional[List[Dict[str, str]]] = None

class Metadatos(BaseModel):
    perfil_aplicado: str
    formato_generado: str
    tiempo_estimado_estudio_minutos: int
    conceptos_clave: List[str]
    prerrequisitos: Optional[List[str]] = None

class EvaluacionCalidad(BaseModel):
    anclaje_fuente_score: float = Field(..., description="Puntuación de fidelidad de 0.0 a 1.0")
    claridad_pedagogica: str = Field(..., example="Alta")
    observaciones: str

class AlmacenamientoOCI(BaseModel):
    bucket: str
    objeto_id: str
    status_upload: str

class AdaptationResponse(BaseModel):
    status: str = Field(default="exito")
    metadatos: Metadatos
    contenido_adaptado: ContenidoAdaptado
    evaluacion_calidad: EvaluacionCalidad
    almacenamiento_oci: AlmacenamientoOCI
