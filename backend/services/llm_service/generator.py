import os
import json
import re
from typing import Dict, Any, List
from google import genai
import sys

# Add parent path to allow importing shared models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared.models import ResultadoEducativo

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
GEMINI_MODEL = "gemini-3.6-flash"

def extraer_json_respuesta(texto: str) -> Dict[str, Any]:
    texto = texto.strip()
    texto = re.sub(r"^```(?:json)?\s*", "", texto, flags=re.I)
    texto = re.sub(r"\s*```$", "", texto)
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        ini = texto.find("{")
        fin = texto.rfind("}")
        if ini >= 0 and fin > ini:
            return json.loads(texto[ini:fin+1])
        raise

def llamar_gemini(prompt: str) -> str:
    if not client:
         raise Exception("GEMINI_API_KEY no configurada en el entorno")
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )
    return response.text

def construir_consulta(perfil, formato, nicho, nivel):
    return (
        f"Conceptos técnicos, definiciones, procedimientos, requisitos y ejemplos "
        f"necesarios para enseñar este documento a un perfil {perfil}, "
        f"en formato {formato}, contexto {nicho}, nivel {nivel}."
    )

def generar_contenido_llm(perfil: str, formato: str, nicho: str, nivel: str, recuperados: List[Dict[str, Any]]):
    contexto = "\n\n".join(
        f"[FUENTE {r['chunk_id']}]\n{r['texto']}" for r in recuperados
    )

    prompt = f"""
Eres el motor pedagógico de NuevaMente.

Tu tarea es transformar EXCLUSIVAMENTE la evidencia recuperada del documento
en material educativo. No inventes características, cifras, pasos, requisitos
ni definiciones que no estén respaldados por la evidencia.

PARÁMETROS:
- Perfil destinatario: {perfil}
- Formato pedagógico: {formato}
- Nicho/contexto: {nicho}
- Nivel de detalle: {nivel}

EVIDENCIA RAG:
{contexto}

Devuelve ÚNICAMENTE JSON válido con esta estructura:
{{
  "status": "exito",
  "metadatos": {{
    "perfil_aplicado": "{perfil}",
    "formato_generado": "{formato}",
    "tiempo_estimado_estudio_minutos": 10,
    "conceptos_clave": ["..."],
    "prerrequisitos": ["..."]
  }},
  "contenido_adaptado": {{
    "titulo": "...",
    "introduccion_contextualizada": "...",
    "items": []
  }},
  "evaluacion_calidad": {{
    "fidelidad_fuente": "Alta/Media/Baja",
    "claridad_pedagogica": "Alta/Media/Baja",
    "observaciones": "..."
  }},
  "fuentes_recuperadas": {[r['chunk_id'] for r in recuperados]}
}}

Adapta la estructura interna de "items" al formato solicitado:
- Flashcards: frente, dorso, pista_didactica.
- Quiz: pregunta, opciones, respuesta_correcta, justificacion.
- Tutorial: paso, titulo, explicacion.
- Resumen ejecutivo: punto, explicacion.
- Guion: seccion, narracion.

No uses Markdown alrededor del JSON.
"""
    bruto = llamar_gemini(prompt)
    data = extraer_json_respuesta(bruto)
    validado = ResultadoEducativo.model_validate(data)
    return validado.model_dump()

def revisar_fidelidad(resultado: Dict[str, Any], recuperados: List[Dict[str, Any]]) -> Dict[str, Any]:
    evidencia = "\n\n".join(
        f"[FUENTE {r['chunk_id']}] {r['texto']}" for r in recuperados
    )

    prompt = f"""
Actúa como revisor de fidelidad de un sistema RAG.

EVIDENCIA:
{evidencia}

CONTENIDO GENERADO:
{json.dumps(resultado, ensure_ascii=False)}

Evalúa si las afirmaciones técnicas están respaldadas por la evidencia.
Devuelve ÚNICAMENTE JSON válido:
{{
  "veredicto": "APROBADO" o "REVISAR",
  "fidelidad_estimada": 0.9,
  "hallazgos": ["..."],
  "recomendacion": "..."
}}

No inventes evidencia.
"""
    revision = extraer_json_respuesta(llamar_gemini(prompt))
    return revision
