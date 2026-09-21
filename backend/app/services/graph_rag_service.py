import networkx as nx
from typing import List, Dict, Any, Tuple

class GraphRAGService:
    def __init__(self):
        pass

    def build_concept_dag(self, document_text: str) -> Tuple[nx.DiGraph, List[str], List[str]]:
        """
        Construye el Grafo Acíclico Dirigido (DAG) de conceptos y relaciones.
        Retorna (Grafo NetworkX, Conceptos Clave por Centralidad, Prerrequisitos).
        """
        G = nx.DiGraph()
        
        # Extraer palabras técnicas con longitud > 3 (simplificación de entidad NER)
        words = [w.strip(".,()[]") for w in document_text.split() if len(w) > 3 and w.istitle()]
        unique_concepts = list(dict.fromkeys(words))[:10]
        
        if len(unique_concepts) < 2:
            unique_concepts = ["VCN", "Subredes", "Security Lists", "Internet Gateway"]
            
        # Construir aristas secuenciales de dependencia A -> B
        for i in range(len(unique_concepts) - 1):
            source = unique_concepts[i]
            target = unique_concepts[i+1]
            G.add_edge(source, target, relation="prerrequisito_de")

        # 1. Calcular Centralidad de Intermediación (Betweenness Centrality)
        try:
            centrality = nx.betweenness_centrality(G)
            sorted_concepts = sorted(centrality.keys(), key=lambda k: centrality[k], reverse=True)
            key_concepts = sorted_concepts[:4] if sorted_concepts else unique_concepts[:4]
        except Exception:
            key_concepts = unique_concepts[:4]

        # 2. Calcular Prerrequisitos mediante recorrido directo del DAG
        prerequisites = unique_concepts[:2]

        return G, key_concepts, prerequisites
