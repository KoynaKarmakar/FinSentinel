from typing import List, Optional

from sentence_transformers import CrossEncoder

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

_reranker: Optional[CrossEncoder] = None


def _get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(settings.reranker_model)
        logger.info(f"Loaded reranker: {settings.reranker_model}")
    return _reranker


def rerank(query: str, candidates: List[dict], top_n: int = 3) -> List[dict]:
    if not candidates:
        return []
    reranker = _get_reranker()
    pairs = [(query, c["text"]) for c in candidates]
    scores = reranker.predict(pairs)
    scored = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [{**cand, "rerank_score": float(score)} for cand, score in scored[:top_n]]
