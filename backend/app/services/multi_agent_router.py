import re
from typing import List

class AgentProfile:
    def __init__(self, name: str, description: str, keywords: List[str]):
        self.name = name
        self.description = description
        self.keywords = [kw.lower() for kw in keywords]

class MultiAgentRouter:
    """
    Enrutador Inteligente (Traffic Cop) que lee el requerimiento del usuario
    y decide qué agente (LLM) es el más óptimo, rápido y económico para la tarea.
    """
    def __init__(self):
        self.agents = [
            AgentProfile(
                name="GEMINI",
                description="Deep Research & Multimodal. Investigaciones complejas, análisis pesado.",
                keywords=["investigar", "análisis profundo", "informe", "sintetizar", "documentar", "comparar datos", "visión multimodal", "pdf pesado", "tutorial", "investigacion"]
            ),
            AgentProfile(
                name="GROQ",
                description="Fast Generation & Multimodal Hybrid. Generación rápida de contenido formateado.",
                keywords=["flashcard", "tarjetas de estudio", "quiz", "cuestionario", "examen corto", "generar lista", "resumen rápido", "estructurar datos", "resumen"]
            ),
            AgentProfile(
                name="GROK",
                description="Conversacional, Voz & Workflows. Chats interactivos y flujos de tiempo real.",
                keywords=["voz", "audio", "automatizar", "flujo de trabajo", "workflow", "chatbot interactivo", "charla fluida", "integraciones"]
            ),
            AgentProfile(
                name="CEREBRAS",
                description="Ultra-Low Latency. Respuestas inmediatas y de baja latencia.",
                keywords=["respuesta inmediata", "tiempo real", "latencia cero", "validación rápida", "clasificación exprés"]
            ),
            AgentProfile(
                name="QWEN_VL",
                description="Análisis multimodal especializado, procesamiento de imágenes y diagramas.",
                keywords=["leer imagen", "analizar gráfico", "ocr", "extraer texto de foto", "diagrama", "esquema visual", "infografia"]
            ),
            AgentProfile(
                name="OPENROUTER",
                description="Pre-Processing & File Fetcher. Ingesta de múltiples archivos.",
                keywords=["traer archivos", "múltiples documentos", "consolidar fuentes", "parsear archivos", "ingesta masiva"]
            ),
            AgentProfile(
                name="OLLAMA",
                description="Local & Connection Fallback. Respaldo sin conexión.",
                keywords=["fallback", "sin conexión", "backup", "respuesta básica económica", "chat económico", "offline", "local"]
            )
        ]

    def route_task(self, output_format: str, task_description: str = "", is_offline: bool = False) -> str:
        """
        Retorna el nombre del agente (ej. 'GROQ', 'GEMINI') que mejor se adapta a la tarea.
        """
        if is_offline:
            return "OLLAMA"
            
        combined_text = f"{output_format} {task_description}".lower()
        
        best_agent = "GEMINI" # Fallback por defecto si no hay coincidencias (es el más capaz)
        max_score = 0
        
        for agent in self.agents:
            score = 0
            for kw in agent.keywords:
                # Usamos regex para buscar la palabra completa o simplemente contenida
                if kw in combined_text:
                    score += 1
            
            if score > max_score:
                max_score = score
                best_agent = agent.name
                
        return best_agent
