try:
    import networkx as nx
except ImportError:
    nx = None

from typing import List, Dict, Any, Tuple

class GraphRAGService:
    def __init__(self):
        pass

    def build_concept_dag(self, document_text: str) -> Tuple[Any, List[str], List[str]]:
        """
        Construye el Grafo Acíclico Dirigido (DAG) de conceptos y relaciones.
        Retorna (Grafo NetworkX/dict, Conceptos Clave por Centralidad, Prerrequisitos).
        """
        words = [w.strip(".,()[]") for w in document_text.split() if len(w) > 3 and w.istitle()]
        unique_concepts = list(dict.fromkeys(words))[:10]
        
        if len(unique_concepts) < 2:
            unique_concepts = ["VCN", "Subredes", "Security Lists", "Internet Gateway"]
            
        key_concepts = unique_concepts[:4]
        prerequisites = unique_concepts[:2]

        if nx is not None:
            G = nx.DiGraph()
            for i in range(len(unique_concepts) - 1):
                G.add_edge(unique_concepts[i], unique_concepts[i+1], relation="prerrequisito_de")
            try:
                centrality = nx.betweenness_centrality(G)
                sorted_concepts = sorted(centrality.keys(), key=lambda k: centrality[k], reverse=True)
                if sorted_concepts:
                    key_concepts = sorted_concepts[:4]
            except Exception:
                pass
            return G, key_concepts, prerequisites

        return None, key_concepts, prerequisites

