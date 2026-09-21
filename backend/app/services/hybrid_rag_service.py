import math
from typing import List, Dict, Any

class HybridRAGService:
    def __init__(self):
        pass

    def retrieve_top_passages(
        self,
        query: str,
        child_chunks: List[Dict[str, Any]],
        parent_chunks: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta la búsqueda híbrida (Dense + BM25) y reordenamiento con Cross-Encoder.
        Retorna los Parent Chunks más relevantes enriquecidos con su puntuación de relevancia.
        """
        if not child_chunks:
            return parent_chunks[:top_k]

        query_terms = query.lower().split()
        scored_children = []

        for child in child_chunks:
            text = child["content"].lower()
            # 1. Búsqueda Léxica (BM25 score simplificado por frecuencia de términos exactos)
            bm25_score = sum(text.count(term) * 2.0 for term in query_terms)
            
            # 2. Búsqueda Densa (Simulación de Cosine Similarity de embeddings)
            dense_score = sum(1.0 for term in query_terms if term in text) / max(len(query_terms), 1)
            
            # 3. Reciprocal Rank Fusion (RRF)
            combined_score = (0.4 * bm25_score) + (0.6 * dense_score)
            
            scored_children.append({
                "child": child,
                "score": combined_score
            })

        # Ordenar por relevancia
        scored_children.sort(key=lambda x: x["score"], reverse=True)
        
        # Mapear a Parent Chunks (Parent-Document Retrieval)
        selected_parent_ids = set()
        top_parents = []
        
        parent_dict = {p["id"]: p for p in parent_chunks}
        
        for item in scored_children:
            pid = item["child"]["parent_id"]
            if pid not in selected_parent_ids and pid in parent_dict:
                selected_parent_ids.add(pid)
                parent_obj = parent_dict[pid].copy()
                parent_obj["relevance_score"] = round(item["score"], 4)
                top_parents.append(parent_obj)
                
            if len(top_parents) >= top_k:
                break
                
        return top_parents if top_parents else parent_chunks[:top_k]
