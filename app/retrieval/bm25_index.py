# app/retrieval/bm25_index.py
import os
import pickle
from typing import List, Optional

from rank_bm25 import BM25Okapi
from qdrant_client import QdrantClient

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

_index: Optional[BM25Okapi] = None
_corpus: List[str] = []
_metadata_registry: List[dict] = []  # NEW: Tracks structural locations alongside text indexing


def build_and_save_index() -> int:
    global _index, _corpus, _metadata_registry
    
    # Scroll and retrieve entire record arrays directly from local storage engine
    from app.retrieval.qdrant_store import get_client
    client = get_client()
    results, _ = client.scroll(
        collection_name=settings.qdrant_collection,
        limit=10000,
        with_payload=True,
    )
    
    if not results:
        logger.warning("No chunks in Qdrant — BM25 index not built")
        return 0
        
    # Isolate textual strings from metadata tracking payloads cleanly
    _corpus = [r.payload["text"] for r in results]
    _metadata_registry = [
        {
            "source": r.payload.get("source", ""),
            "doc_type": r.payload.get("doc_type", ""),
            "page": r.payload.get("page", 0),
            "chapter": r.payload.get("chapter", "N/A"),
            "section": r.payload.get("section", "N/A"),
            "subsection": r.payload.get("subsection", "N/A"),
        }
        for r in results
    ]
    
    tokenized = [text.lower().split() for text in _corpus]
    _index = BM25Okapi(tokenized)
    
    os.makedirs(os.path.dirname(settings.bm25_pickle_path), exist_ok=True)
    with open(settings.bm25_pickle_path, "wb") as f:
        pickle.dump({
            "index": _index, 
            "corpus": _corpus,
            "metadata": _metadata_registry # Save metadata references into pickle binary
        }, f)
        
    logger.info(f"BM25 index built with {len(_corpus)} docs → {settings.bm25_pickle_path}")
    return len(_corpus)


def load_index() -> bool:
    global _index, _corpus, _metadata_registry
    if not os.path.exists(settings.bm25_pickle_path):
        logger.info("No BM25 pickle found — will build on first ingest")
        return False
    with open(settings.bm25_pickle_path, "rb") as f:
        data = pickle.load(f)
    _index = data["index"]
    _corpus = data["corpus"]
    _metadata_registry = data.get("metadata", []) # Load matching metadata mappings
    logger.info(f"BM25 index loaded: {len(_corpus)} docs from {settings.bm25_pickle_path}")
    return True


def bm25_search(query: str, top_k: int = 10) -> List[dict]:
    global _index, _corpus, _metadata_registry
    if _index is None:
        load_index()
    if _index is None or not _corpus:
        return []
        
    tokens = query.lower().split()
    scores = _index.get_scores(tokens)
    indexed = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
    
    results = []
    for rank, (i, s) in enumerate(indexed):
        # Merge text data with structural tracking components seamlessly
        meta = _metadata_registry[i] if i < len(_metadata_registry) else {}
        results.append({
            "text": _corpus[i],
            "score": float(s),
            "rank": rank,
            "source": meta.get("source", ""),
            "doc_type": meta.get("doc_type", ""),
            "page": meta.get("page", 0),
            "chapter": meta.get("chapter", "N/A"),
            "section": meta.get("section", "N/A"),
            "subsection": meta.get("subsection", "N/A"),
        })
    return results