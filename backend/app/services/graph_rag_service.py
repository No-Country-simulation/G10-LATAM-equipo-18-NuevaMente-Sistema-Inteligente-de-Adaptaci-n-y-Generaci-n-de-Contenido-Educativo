import json
import logging
try:
    import networkx as nx
except ImportError:
    nx = None

from typing import List, Dict, Any, Tuple
from app.infrastructure.gemini_client import GeminiClient

logger = logging.getLogger("GraphRAGService")

class GraphRAGService:
    def __init__(self):
        self.gemini_client = GeminiClient()

    def build_concept_dag(self, document_text: str) -> Tuple[Any, List[str], List[str]]:
        """
        Construye el Grafo Acíclico Dirigido (DAG) de conceptos y relaciones.
        Utiliza Gemini para extraer entidades y relaciones de manera semántica, 
        convirtiéndolo en un verdadero grafo de conocimiento.
        Retorna (Grafo NetworkX/dict, Conceptos Clave por Centralidad, Prerrequisitos).
        """
        prompt = f"""
        Analiza el siguiente texto y extrae un Knowledge Graph. 
        Identifica los conceptos clave y las relaciones entre ellos, enfocándote en dependencias o prerrequisitos.
        Devuelve el resultado ÚNICAMENTE en formato JSON estricto con la siguiente estructura:
        {{
            "concepts": ["Concepto 1", "Concepto 2", ...],
            "relationships": [
                {{"source": "Concepto 1", "target": "Concepto 2", "relation": "prerrequisito_de"}}
            ]
        }}
        Solo incluye un máximo de 10 conceptos más relevantes para ahorrar tokens.
        
        Texto:
        {document_text[:3000]}
        """
        
        key_concepts = ["VCN", "Subredes", "Security Lists", "Internet Gateway"]
        prerequisites = ["VCN", "Subredes"]
        
        try:
            response_text = self.gemini_client.generate_content(
                prompt=prompt,
                system_instruction="Eres un experto en extracción de conocimiento. Devuelve siempre JSON válido.",
                json_output=True
            )
            
            # Limpiar posible markdown en la respuesta
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
                
            data = json.loads(response_text)
            unique_concepts = data.get("concepts", [])
            relationships = data.get("relationships", [])
            
            if unique_concepts:
                key_concepts = unique_concepts[:4]
                prerequisites = unique_concepts[:2]
        except Exception as e:
            logger.error(f"Error al extraer grafo con Gemini: {e}. Activando Fallback con Jina AI.")
            # Fallback logic: Utilizar Embeddings de Jina AI para extraer los conceptos clave (Similitud Semántica)
            try:
                from app.services.embedding_service import EmbeddingService
                import numpy as np
                
                # Inicializar servicio de embeddings forzando el proveedor Jina
                jina_embedder = EmbeddingService(provider="jina")
                
                # 1. Obtener candidatos (palabras relevantes). Extraemos menos candidatos para Jina (la mitad de lo normal).
                candidate_words = list(dict.fromkeys([w.strip(".,()[]") for w in document_text.split() if len(w) > 4 and w.istitle()]))
                candidate_words = candidate_words[:max(1, len(candidate_words) // 2)]
                
                if not candidate_words:
                    candidate_words = ["VCN", "Subredes", "Security Lists", "Internet Gateway"]
                
                # 2. Embeddings del texto completo y los candidatos. Pasamos MUCHO menos texto (50% chars) para ahorrar Jina.
                doc_embedding = np.array(jina_embedder.embed_text(document_text[:max(1, len(document_text) // 2)]))
                candidates_embeddings = np.array(jina_embedder.embed_batch(candidate_words))
                
                # 3. Similitud del coseno (Producto punto ya que los embeddings suelen estar normalizados)
                norm_doc = np.linalg.norm(doc_embedding)
                norm_cands = np.linalg.norm(candidates_embeddings, axis=1)
                similarities = np.dot(candidates_embeddings, doc_embedding) / (norm_cands * norm_doc)
                
                # 4. Seleccionar los top 10
                top_indices = similarities.argsort()[-10:][::-1]
                unique_concepts = [candidate_words[i] for i in top_indices]
                
            except Exception as jina_err:
                logger.error(f"Error en Fallback de Jina: {jina_err}. Usando reglas básicas.")
                words = [w.strip(".,()[]") for w in document_text.split() if len(w) > 3 and w.istitle()]
                unique_concepts = list(dict.fromkeys(words))[:10]
                if len(unique_concepts) < 2:
                    unique_concepts = ["VCN", "Subredes", "Security Lists", "Internet Gateway"]
                    
            relationships = [{"source": unique_concepts[i], "target": unique_concepts[i+1], "relation": "prerrequisito_de"} for i in range(len(unique_concepts)-1)]
        
        if nx is not None:
            G = nx.DiGraph()
            for concept in unique_concepts:
                G.add_node(concept)
                
            for rel in relationships:
                src = rel.get("source")
                tgt = rel.get("target")
                G.add_edge(src, tgt, relation=rel.get("relation", "relacionado_con"))
                
            try:
                centrality = nx.betweenness_centrality(G)
                sorted_concepts = sorted(centrality.keys(), key=lambda k: centrality[k], reverse=True)
                if sorted_concepts:
                    key_concepts = sorted_concepts[:4]
            except Exception:
                pass
            return G, key_concepts, prerequisites

        return None, key_concepts, prerequisites

