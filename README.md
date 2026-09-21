# G10-LATAM-equipo-18-NuevaMente-Sistema-Inteligente
Proyecto 1 – 🎓 NuevaMente – Sistema Inteligente  de Adaptación y Generación de Contenido  Educativo



## Descripción del proyecto 
Crear una solución inteligente capaz de ingerir documentaciones técnicas, manuales de software, 
artículos o bases de conocimiento y transformarlos automáticamente en contenidos educativos 
personalizados y estructurados según el perfil del destinatario, la industria de aplicación y el formato 
pedagógico de salida elegido. 

# NuevaMente - Microservices

This project is a microservices-based application that extracts information from documents (PDF, TXT, MD) using RAG (Retrieval-Augmented Generation) and generates educational material using the Gemini LLM.

## Architecture Overview

The project is split into two main components: **Frontend** and **Backend**.

### Frontend
- Located in `frontend/`
- Built with **Gradio**, providing a user-friendly web interface.
- It accepts the user's document, preferred profile, format, and context, and sends an HTTP POST request to the Backend API Gateway.

### Backend
- Located in `backend/`
- Built with **FastAPI**.
- The `api_gateway/main.py` is the main entry point that routes the work to several specific services:
  - **RAG Service**: Handles text extraction from files and chunks the text. Uses `SentenceTransformer` and `faiss` to convert text into vectors and search for relevant information.
  - **LLM Service**: Connects to the **Gemini API** (`google-genai`). It takes the retrieved vectors and system prompts to generate the educational content and also verifies the fidelity of the generated content against the original document.
  - **Storage Service**: Integrates with Oracle Cloud Infrastructure (**OCI**) Object Storage. It uploads the original documents and the final generated JSON files for safekeeping.
  - **Shared**: Contains Pydantic data models (`models.py`) used across all services to enforce structure.

---

## Prerequisites

You need Python installed, and you must configure your environment variables for Gemini and OCI:

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export OCI_USER_OCID="your-user-ocid"
export OCI_TENANCY_OCID="your-tenancy-ocid"
export OCI_FINGERPRINT="your-fingerprint"
export OCI_REGION="your-region"
export OCI_PRIVATE_KEY="your-private-key-content"
export OCI_NAMESPACE="your-namespace"
export OCI_BUCKET="your-bucket-name"
```

---

## How to Run the Project

You will need to open **two separate terminal windows**—one for the backend and one for the frontend.

### 1. Start the Backend

Open your first terminal and navigate to the backend directory:
```bash
cd lphb/backend
```

Create a virtual environment and install the backend dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the API Gateway:
```bash
cd api_gateway
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The backend is now running and listening on `http://localhost:8000`.

### 2. Start the Frontend

The frontend web interface is protected by basic authentication. By default, the credentials are:
- **Username:** `admin`
- **Password:** `admin`

*(You can override these by setting the `GRADIO_USER` and `GRADIO_PASSWORD` environment variables before starting the frontend).*

Open your second terminal and navigate to the frontend directory:
```bash
cd lphb/frontend
```

Create a virtual environment and install the frontend dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the Gradio application:
```bash
python app.py
```
The UI should now be available at `http://localhost:7860`. You can upload your document here, and the frontend will automatically communicate with the backend!
