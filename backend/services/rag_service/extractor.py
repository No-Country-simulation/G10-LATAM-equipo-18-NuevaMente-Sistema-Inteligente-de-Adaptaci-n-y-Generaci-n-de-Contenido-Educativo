import re
from pathlib import Path
from pypdf import PdfReader
from typing import List

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

def extraer_texto(ruta: str) -> str:
    ruta = Path(ruta)
    ext = ruta.suffix.lower()

    if ext == ".pdf":
        reader = PdfReader(str(ruta))
        paginas = []

        for i, page in enumerate(reader.pages, start=1):
            try:
                texto = page.extract_text(extraction_mode="layout") or ""
            except TypeError:
                texto = page.extract_text() or ""

            texto = texto.replace("\x00", "").strip()
            if texto:
                paginas.append(f"\n[PÁGINA {i}]\n{texto}")

        texto_final = "\n".join(paginas)
        if len(texto_final.strip()) < 50:
            raise ValueError("No se pudo extraer suficiente texto del PDF.")
        return texto_final

    if ext in {".md", ".markdown", ".txt"}:
        return ruta.read_text(encoding="utf-8", errors="ignore")

    raise ValueError("Formato no soportado. Utilizá PDF, Markdown o TXT.")

def limpiar_texto(texto: str) -> str:
    texto = texto.replace("\x00", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()

def crear_chunks(texto: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if not texto:
        return []

    chunks = []
    inicio = 0
    while inicio < len(texto):
        fin = min(inicio + chunk_size, len(texto))
        fragmento = texto[inicio:fin].strip()
        if fragmento:
            chunks.append(fragmento)
        if fin == len(texto):
            break
        inicio = max(fin - overlap, inicio + 1)
    return chunks
