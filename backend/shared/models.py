from pydantic import BaseModel
from typing import List, Dict, Any

class Metadatos(BaseModel):
    perfil_aplicado: str
    formato_generado: str
    tiempo_estimado_estudio_minutos: int
    conceptos_clave: List[str]
    prerrequisitos: List[str] = []

class EvaluacionCalidad(BaseModel):
    fidelidad_fuente: str
    claridad_pedagogica: str
    observaciones: str

class ResultadoEducativo(BaseModel):
    status: str = "exito"
    metadatos: Metadatos
    contenido_adaptado: Dict[str, Any]
    evaluacion_calidad: EvaluacionCalidad
    fuentes_recuperadas: List[int] = []
