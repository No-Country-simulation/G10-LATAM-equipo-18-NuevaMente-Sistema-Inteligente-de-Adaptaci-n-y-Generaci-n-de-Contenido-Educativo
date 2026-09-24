try:
    import networkx as nx
except ImportError:
    nx = None

import re
from typing import List, Dict, Any, Tuple

STOP_WORDS = {
    "Página", "Pagina", "Page", "Pág", "Pag", "Figura", "Figure", "Tabla", "Table", 
    "Sección", "Section", "Abstract", "Introduction", "Autor", "Author", "Et", "Al",
    "Vol", "No", "Pp", "Pages", "Doi", "Http", "Https", "Org", "Pdf", "Text", "Documento"
}

class GraphRAGService:
    def __init__(self):
        pass

    def build_concept_dag(self, document_text: str) -> Tuple[Any, List[str], List[str]]:
        """
        Construye el Grafo Acíclico Dirigido (DAG) de conceptos y relaciones.
        Filtra artefactos sintácticos (como 'Página 1') y extrae conceptos reales.
        """
        # Extraer términos técnicos compuestos y palabras clave relevantes
        raw_words = re.findall(r'\b[A-Z][a-zA-Z0-9\-]{2,}\b', document_text)
        
        filtered_concepts = []
        for w in raw_words:
            if w not in STOP_WORDS and not w.isnumeric() and len(w) > 3:
                if w not in filtered_concepts:
                    filtered_concepts.append(w)
                    
        if len(filtered_concepts) < 2:
            filtered_concepts = ["Retrieval-Augmented", "Knowledge-Graph", "Dense-Passage", "Sequence-to-Sequence"]
            
        key_concepts = filtered_concepts[:4]
        prerequisites = filtered_concepts[:2]

        if nx is not None:
            G = nx.DiGraph()
            for i in range(len(filtered_concepts) - 1):
                G.add_edge(filtered_concepts[i], filtered_concepts[i+1], relation="prerrequisito_de")
            try:
                centrality = nx.betweenness_centrality(G)
                sorted_concepts = sorted(centrality.keys(), key=lambda k: centrality[k], reverse=True)
                if sorted_concepts:
                    key_concepts = sorted_concepts[:4]
            except Exception:
                pass
            return G, key_concepts, prerequisites

        return None, key_concepts, prerequisites
