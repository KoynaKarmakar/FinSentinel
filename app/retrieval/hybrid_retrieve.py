# app/retrieval/hybrid_retrieve.py
from typing import List, Optional

from app.core.config import settings
from app.core.logger import get_logger
from app.ingestion.embedder import embed_text
from app.retrieval.bm25_index import bm25_search
from app.retrieval.qdrant_store import dense_search
from app.retrieval.reranker import rerank
from app.retrieval.rrf_fusion import rrf_fuse

logger = get_logger(__name__)


def hybrid_retrieve(query: str, doc_type: Optional[str] = None) -> List[dict]:
    # 1. Transform query string into numerical dense coordinates
    query_vector = embed_text(query)
    
    # 2. Query both index tracks (we search top-20 to ensure RRF has a wide candidate pool)
    dense_results = dense_search(query_vector, doc_type=doc_type, top_k=20)
    bm25_results = bm25_search(query, top_k=20)
    
    # 3. Blend rankings together mathematically
    fused = rrf_fuse(dense_results, bm25_results)
    
    # 4. Rerank the fused pool using cross-attention via the PyTorch model
    # Passing the full fused set lets the Cross-Encoder scan all good candidates
    top_reranked = rerank(query, fused, top_n=settings.rerank_top_n)
    
    logger.info(f"Hybrid retrieve complete: {len(top_reranked)} structured chunks optimized for query: '{query[:60]}'")
    return top_reranked