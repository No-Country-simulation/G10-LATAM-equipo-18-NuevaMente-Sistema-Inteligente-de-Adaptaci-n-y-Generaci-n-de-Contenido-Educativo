"""
ingestion.py

Purpose:
    Typed data contracts for the document ingestion and chunking layer.
    Supports structured document chunks, document representation,
    and conversion to RAG hierarchical format (parent/child).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class IngestionOptions(BaseModel):
    """Optional settings for how a document is processed."""
    pdf_extraction_strategy: str = "raw"


class DocumentChunk(BaseModel):
    """Represents a segment of a source document."""
    chunk_id: str
    document_id: str
    text: str
    section_title: Optional[str] = None
    heading_level: Optional[int] = None
    page_number: Optional[int] = None
    embedding: Optional[List[float]] = None


class IngestedDocument(BaseModel):
    """Represents a processed document with text and chunks."""
    document_id: str
    title: str
    source_filename: str
    raw_text: str
    chunks: List[DocumentChunk] = Field(default_factory=list)

    def to_rag_format(self) -> Dict[str, Any]:
        """
        Adapts chunks into the hierarchical Parent-Document format
        expected by HybridRAGService and downstream components.
        """
        parent_chunks = []
        child_chunks = []

        # Group or map chunks to parent-child structure
        for idx, chunk in enumerate(self.chunks):
            p_id = f"parent_{idx}"
            title = chunk.section_title or f"Sección {idx + 1}"

            parent_chunks.append({
                "id": p_id,
                "title": title,
                "breadcrumb": f"{self.title} > {title}",
                "content": chunk.text,
                "metadata": {
                    "source_title": self.title,
                    "section_index": idx,
                    "page_number": chunk.page_number,
                    "heading_level": chunk.heading_level,
                }
            })

            # For smaller child segmentation within this chunk
            words = chunk.text.split()
            step = 150
            if len(words) <= step:
                child_chunks.append({
                    "id": f"{p_id}_child_0",
                    "parent_id": p_id,
                    "breadcrumb": f"[{self.title} > {title}]",
                    "content": chunk.text,
                    "metadata": {
                        "parent_id": p_id,
                        "source": self.title
                    }
                })
            else:
                for c_idx in range(0, len(words), step):
                    chunk_words = words[c_idx:c_idx + step]
                    child_chunks.append({
                        "id": f"{p_id}_child_{c_idx}",
                        "parent_id": p_id,
                        "breadcrumb": f"[{self.title} > {title}]",
                        "content": " ".join(chunk_words),
                        "metadata": {
                            "parent_id": p_id,
                            "source": self.title
                        }
                    })

        return {
            "title": self.title,
            "parent_chunks": parent_chunks,
            "child_chunks": child_chunks,
            "total_parents": len(parent_chunks),
            "total_children": len(child_chunks)
        }
