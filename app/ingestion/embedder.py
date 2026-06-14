from typing import List, Optional

from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

_model: Optional[SentenceTransformer] = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
        logger.info(f"Loaded embedding model: {settings.embedding_model}")
    return _model


def embed_chunks(chunks: List[Document]) -> List[List[float]]:
    model = _get_model()
    texts = [chunk.page_content for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()


def embed_text(text: str) -> List[float]:
    model = _get_model()
    embedding = model.encode([text], show_progress_bar=False, normalize_embeddings=True)
    return embedding[0].tolist()
