import gradio as gr
import requests
import os
import json
import tempfile

# Assuming API Gateway runs locally on port 8000
API_URL = os.getenv("API_URL", "http://localhost:8000")

PERFILES = [
    "Principiante / Transición de Carrera",
    "Desarrollador Junior / Semi Senior",
    "Líder Técnico / Arquitecto",
    "Gestor / Ejecutivo (No Técnico)"
]

FORMATOS = [
    "Guía Práctica Paso a Paso (Tutorial)",
    "Flashcards de Memorización",
    "Quiz Interactivo con Justificaciones",
    "Resumen Ejecutivo (TL;DR)",
    "Guion de Clase / Video"
]

NICHOS = ["General", "Fintech", "Salud", "E-commerce"]
NIVELES = ["Básico", "Didáctico", "Intermedio", "Avanzado"]

def procesar_nuevamente(archivo, perfil, formato, nicho, nivel):
    if not archivo:
        raise gr.Error("Primero cargá un documento PDF, Markdown o TXT.")
        
    ruta = archivo if isinstance(archivo, str) else (archivo.name if hasattr(archivo, 'name') else str(archivo))

    # We send the file and parameters to the API Gateway
    with open(ruta, "rb") as f:
        files = {"file": (os.path.basename(ruta), f)}
        data = {
            "perfil": perfil,
            "formato": formato,
            "nicho": nicho,
            "nivel": nivel
        }
        
        try:
            response = requests.post(f"{API_URL}/generate", files=files, data=data)
            response.raise_for_status()
            res_data = response.json()
            
            resultado = res_data.get("resultado", {})
            resumen_fuentes = res_data.get("evidencia", "")
            
            # Save the JSON locally to allow downloading from Gradio
            temp_json = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w', encoding='utf-8')
            json.dump(resultado, temp_json, ensure_ascii=False, indent=2)
            temp_json.close()
            
            return resultado, resumen_fuentes, temp_json.name
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = e.response.json()
                if "detail" in error_data:
                    error_msg = error_data["detail"]
            except Exception:
                error_msg = e.response.text or error_msg
            raise gr.Error(f"Error del servidor: {error_msg}")
        except Exception as e:
            raise gr.Error(f"Error conectando al backend: {str(e)}")

with gr.Blocks(title="NuevaMente") as demo:
    gr.Markdown(
        '''
        # 🎓 NuevaMente
        ### De documentación técnica a experiencias de aprendizaje personalizadas
        Cargá un documento y elegí cómo querés aprender su contenido.
        '''
    )

    with gr.Row():
        archivo = gr.File(
            label="📄 Documento técnico",
            file_types=[".pdf", ".md", ".markdown", ".txt"],
            type="filepath"
        )
        with gr.Column():
            perfil = gr.Dropdown(PERFILES, value=PERFILES[0], label="👤 Perfil")
            formato = gr.Dropdown(FORMATOS, value=FORMATOS[1], label="📚 Formato")
            nicho = gr.Dropdown(NICHOS, value=NICHOS[0], label="🏢 Contexto")
            nivel = gr.Dropdown(NIVELES, value=NIVELES[1], label="🎯 Nivel")

    generar = gr.Button("✨ Generar contenido", variant="primary")

    with gr.Tab("📖 Resultado"):
        salida_json = gr.JSON(label="Paquete educativo")

    with gr.Tab("🔎 Evidencia RAG"):
        fuentes = gr.Textbox(label="Fragmentos recuperados", lines=18)

    descarga = gr.File(label="⬇️ Descargar JSON")

    generar.click(
        fn=procesar_nuevamente,
        inputs=[archivo, perfil, formato, nicho, nivel],
        outputs=[salida_json, fuentes, descarga]
    )

if __name__ == "__main__":
    gradio_user = os.getenv("GRADIO_USER", "admin")
    gradio_pass = os.getenv("GRADIO_PASSWORD", "admin")
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860, auth=(gradio_user, gradio_pass))
