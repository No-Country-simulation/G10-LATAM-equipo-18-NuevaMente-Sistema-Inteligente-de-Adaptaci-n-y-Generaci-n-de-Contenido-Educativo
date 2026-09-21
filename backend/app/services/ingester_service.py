import re
from typing import List, Dict, Any

class IngesterService:
    def __init__(self, child_chunk_size: int = 150, parent_chunk_size: int = 1200):
        self.child_chunk_size = child_chunk_size
        self.parent_chunk_size = parent_chunk_size

    def parse_and_chunk_document(self, content: str, title: str) -> Dict[str, Any]:
        """
        Ejecuta el parsing consciente de estructura (Layout-Aware / Markdown AST) 
        y la segmentación jerárquica Parent-Document (Small-to-Big Retrieval).
        """
        # 1. Normalizar saltos de línea y formateo
        clean_content = re.sub(r'\r\n', '\n', content)
        
        # 2. Extraer secciones por encabezados de Markdown (H1, H2, H3)
        sections = re.split(r'(?=\n#{1,3}\s)', clean_content)
        
        parent_chunks = []
        child_chunks = []
        
        for idx, sec in enumerate(sections):
            if not sec.strip():
                continue
            
            # Encabezado jerárquico
            header_match = re.match(r'^(#{1,3})\s+(.*)', sec.strip())
            header_title = header_match.group(2) if header_match else f"Sección {idx+1}"
            
            parent_id = f"parent_{idx}"
            parent_chunk = {
                "id": parent_id,
                "title": header_title,
                "breadcrumb": f"{title} > {header_title}",
                "content": sec.strip(),
                "metadata": {
                    "source_title": title,
                    "section_index": idx
                }
            }
            parent_chunks.append(parent_chunk)
            
            # Segmentar en child chunks (pequeños para búsqueda vectorial rápida)
            words = sec.strip().split()
            step = self.child_chunk_size
            for c_idx in range(0, len(words), step):
                chunk_words = words[c_idx:c_idx + step]
                chunk_text = " ".join(chunk_words)
                child_chunks.append({
                    "id": f"{parent_id}_child_{c_idx}",
                    "parent_id": parent_id,
                    "breadcrumb": f"[{title} > {header_title}]",
                    "content": chunk_text,
                    "metadata": {
                        "parent_id": parent_id,
                        "source": title
                    }
                })

        return {
            "title": title,
            "parent_chunks": parent_chunks,
            "child_chunks": child_chunks,
            "total_parents": len(parent_chunks),
            "total_children": len(child_chunks)
        }

    def map_reduce_summarize(self, parent_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simula o procesa la etapa Map-Reduce para condensar documentos muy extensos.
        Fase Map: Extracción de facts atómicos por sección.
        Fase Reduce: Síntesis global consolidada sin duplicación.
        """
        extracted_claims = []
        for p in parent_chunks:
            # Map step: Extrae las primeras oraciones clave
            sentences = [s.strip() for s in p["content"].split('.') if len(s.strip()) > 15]
            if sentences:
                extracted_claims.append(sentences[0])
                
        # Reduce step: Consolidación
        unified_summary = " ".join(extracted_claims[:5])
        return {
            "claims_extraidos": extracted_claims,
            "resumen_consolidado": unified_summary
        }
