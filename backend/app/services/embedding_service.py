"""
embedding_service.py

Purpose:
    Generates vector embeddings for text using a configurable provider.
    Supports Google Gemini API, Jina AI API, and a local sentence-transformers
    model. Every provider is forced to the same output dimension
    (settings.EMBEDDING_DIMENSIONS) so vectors from any provider are
    interchangeable across FAISS and a future pgvector column.

    On failure, calls are retried with exponential backoff; API batch calls
    additionally shrink in size and retry if the provider rejects a large
    batch. There is no cross-provider fallback: if the configured provider
    ultimately fails, the call raises instead of silently switching provider
    or truncating text, since either would corrupt the resulting index.

Input:
    - text (str) or list of texts (List[str]) to embed.
    - Provider and model resolved from `settings` at instantiation time,
      overridable via constructor arguments.

Output:
    - Single embedding: List[float]
    - Batch embeddings: List[List[float]]
    - `model_name` (str): tag identifying provider + model + dimension
      (e.g. "models/gemini-embedding-001@768"), stored as collection
      metadata in the vector store to enforce query/index compatibility.
"""

import logging
import time
from typing import List, Optional

import numpy as np

# google.generativeai is imported lazily inside its method to avoid
# ModuleNotFoundError when the package is not installed.

from app.core.config import settings
from app.infrastructure.jina_client import JinaClient, TASK_PASSAGE, TASK_QUERY

logger = logging.getLogger(__name__)

# Task type used for Gemini embedding calls — "RETRIEVAL_DOCUMENT" for indexing,
# "RETRIEVAL_QUERY" for query-time embedding.
_GEMINI_TASK_DOCUMENT = "RETRIEVAL_DOCUMENT"
_GEMINI_TASK_QUERY = "RETRIEVAL_QUERY"

# Retry/backoff defaults for single-call API requests (Gemini).
_MAX_RETRIES = 3
_BASE_DELAY_SECONDS = 1.0


class EmbeddingService:
    """
    Unified embedding interface. Resolves provider and model at init time
    and exposes a consistent `embed_text` / `embed_batch` API regardless
    of the underlying provider.
    """

    def __init__(
        self,
        method: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        # Resolve method and provider from settings if not explicitly overridden.
        self.method = method or settings.EMBEDDING_METHOD
        self.provider = provider or settings.EMBEDDING_API_PROVIDER
        self.dimensions = settings.EMBEDDING_DIMENSIONS

        # model_id is the identifier sent to the provider's API.
        # model_name is the compatibility tag stored in the vector store —
        # it includes the dimension so switching EMBEDDING_DIMENSIONS forces
        # a fresh index instead of silently mixing incompatible vectors.
        if self.method == "local":
            self.model_id = settings.LOCAL_EMBEDDING_MODEL
            self._model = self._load_local_model()
        else:
            self.model_id = settings.EMBEDDING_API_MODELS.get(
                self.provider, settings.DEFAULT_EMBEDDING_MODEL
            )
            self._model = None  # API providers are stateless (HTTP calls)

        self.model_name = f"{self.model_id}@{self.dimensions}"

        # Reused across calls instead of creating a new client per request.
        self._gemini_client = None
        self._jina_client = JinaClient(api_key=settings.JINA_API_KEY)

        logger.info(
            "EmbeddingService initialized | method=%s provider=%s model=%s dimensions=%d",
            self.method,
            self.provider,
            self.model_name,
            self.dimensions,
        )

    # ── Public API ─────────────────────────────────────────────────────────────

    def embed_text(self, text: str, is_query: bool = False) -> List[float]:
        """
        Embeds a single text string.

        Args:
            text: The text to embed.
            is_query: True when embedding a search query (affects provider task type).

        Returns:
            Embedding vector as a list of floats, L2-normalized, at settings.EMBEDDING_DIMENSIONS.
        """
        return self.embed_batch([text], is_query=is_query)[0]

    def embed_batch(self, texts: List[str], is_query: bool = False) -> List[List[float]]:
        """
        Embeds a list of texts, batching where the provider supports it.

        Args:
            texts: Texts to embed.
            is_query: True when embedding search queries rather than documents
                to index (affects provider task type).

        Returns:
            List of embedding vectors, one per input text, L2-normalized,
            each of length settings.EMBEDDING_DIMENSIONS.
        """
        if not texts:
            return []

        if self.method == "local":
            vectors = self._embed_local(texts)
        elif self.provider == "gemini":
            vectors = [self._embed_gemini_with_retry(t, is_query=is_query) for t in texts]
        elif self.provider == "jina":
            vectors = self._embed_jina_in_batches(texts, is_query=is_query)
        else:
            raise ValueError(f"Unknown embedding provider: {self.provider}")

        self._validate_dimensions(vectors)
        return self._normalize(vectors)

    # ── Private: Gemini ────────────────────────────────────────────────────────
    # Uses google-genai v2 SDK: Client(api_key=...) + client.models.embed_content(...)
    # No public batch endpoint is exposed by the SDK, so calls stay sequential;
    # each one is retried independently on transient failures.

    def _get_gemini_client(self):
        if self._gemini_client is None:
            from google import genai  # noqa: PLC0415
            self._gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self._gemini_client

    def _embed_gemini_with_retry(self, text: str, is_query: bool) -> List[float]:
        last_error: Exception = None
        for attempt in range(_MAX_RETRIES + 1):
            try:
                return self._embed_gemini(text, is_query=is_query)
            except Exception as exc:
                last_error = exc
                if attempt < _MAX_RETRIES:
                    delay = _BASE_DELAY_SECONDS * (2 ** attempt)
                    logger.warning(
                        "Gemini embedding failed (attempt %d/%d): %s. Retrying in %.1fs.",
                        attempt + 1, _MAX_RETRIES + 1, exc, delay,
                    )
                    time.sleep(delay)
        raise RuntimeError(f"Gemini embedding failed after retries: {last_error}") from last_error

    def _embed_gemini(self, text: str, is_query: bool) -> List[float]:
        from google.genai import types  # noqa: PLC0415

        client = self._get_gemini_client()
        task_type = _GEMINI_TASK_QUERY if is_query else _GEMINI_TASK_DOCUMENT

        result = client.models.embed_content(
            model=self.model_id,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=self.dimensions,
            ),
        )
        return result.embeddings[0].values

    # ── Private: Jina ──────────────────────────────────────────────────────────
    # Sent in configurable-size batches (settings.EMBEDDING_BATCH_SIZE). If a
    # batch fails after its own retries, it is split in half and retried —
    # down to single-text calls — instead of falling back to another provider.

    def _embed_jina_in_batches(self, texts: List[str], is_query: bool) -> List[List[float]]:
        task = TASK_QUERY if is_query else TASK_PASSAGE
        batch_size = settings.EMBEDDING_BATCH_SIZE
        return self._embed_jina_chunk(texts, task, batch_size)

    def _embed_jina_chunk(self, texts: List[str], task: str, batch_size: int) -> List[List[float]]:
        if not texts:
            return []

        results: List[List[float]] = []
        for start in range(0, len(texts), batch_size):
            piece = texts[start:start + batch_size]
            try:
                results.extend(
                    self._jina_client.embed_batch(
                        piece,
                        model_name=self.model_id,
                        dimensions=self.dimensions,
                        task=task,
                    )
                )
            except Exception as exc:
                if batch_size == 1:
                    raise RuntimeError(f"Jina embedding failed for a single text: {exc}") from exc
                logger.warning(
                    "Jina batch of %d failed (%s). Halving batch size and retrying.",
                    len(piece), exc,
                )
                results.extend(self._embed_jina_chunk(piece, task, max(1, batch_size // 2)))

        return results

    # ── Private: Local ─────────────────────────────────────────────────────────

    def _load_local_model(self):
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            logger.info("Loading local embedding model: %s", self.model_id)
            return SentenceTransformer(self.model_id)
        except ImportError:
            logger.error(
                "sentence-transformers not installed. "
                "Run: uv add sentence-transformers"
            )
            return None

    def _embed_local(self, texts: List[str]) -> List[List[float]]:
        if self._model is None:
            raise RuntimeError(
                "Local embedding model is not available. "
                "Install sentence-transformers or switch to an API provider."
            )
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    # ── Private: Validation & normalization ───────────────────────────────────

    def _validate_dimensions(self, vectors: List[List[float]]) -> None:
        """Ensures every vector matches settings.EMBEDDING_DIMENSIONS before it
        can reach the vector store — a silent mismatch there is much harder
        to trace back to its source than failing here."""
        for vector in vectors:
            if len(vector) != self.dimensions:
                raise RuntimeError(
                    f"Embedding dimension mismatch: provider '{self.provider}' "
                    f"(model '{self.model_id}') returned {len(vector)} dimensions, "
                    f"expected {self.dimensions}. Local models have a fixed output "
                    f"size — check LOCAL_EMBEDDING_MODEL matches EMBEDDING_DIMENSIONS."
                )

    @staticmethod
    def _normalize(vectors: List[List[float]]) -> List[List[float]]:
        """L2-normalizes vectors so cosine and inner-product similarity agree,
        regardless of which store (FAISS or a future pgvector column) consumes them."""
        array = np.array(vectors, dtype=np.float32)
        norms = np.linalg.norm(array, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        return (array / norms).tolist()