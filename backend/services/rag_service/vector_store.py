import faiss
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
TOP_K = 6

class VectorRAG:
    def __init__(self):
        self.chunks = []
        self.index = None

    def indexar(self, chunks: List[str]):
        if not chunks:
            raise ValueError("No hay fragmentos para indexar.")

        self.chunks = chunks
        vectors = embedding_model.encode(
            chunks, normalize_embeddings=True, show_progress_bar=False
        ).astype("float32")

        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)
        return len(chunks)

    def buscar(self, consulta: str, k: int = TOP_K) -> List[Dict[str, Any]]:
        if self.index is None:
            raise ValueError("El Vector Store todavía no fue creado.")

        q = embedding_model.encode(
            [consulta], normalize_embeddings=True, show_progress_bar=False
        ).astype("float32")

        k = min(k, len(self.chunks))
        scores, ids = self.index.search(q, k)

        return [
            {"chunk_id": int(idx), "score": float(score), "texto": self.chunks[idx]}
            for score, idx in zip(scores[0], ids[0]) if idx >= 0
        ]
