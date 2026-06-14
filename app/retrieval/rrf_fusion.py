# app/retrieval/rrf_fusion.py
from typing import Dict, List


def rrf_fuse(
    dense_results: List[dict],
    bm25_results: List[dict],
    k: int = 60,
) -> List[dict]:
    scores: Dict[str, float] = {}
    meta: Dict[str, dict] = {}

    # 1. Process dense vector findings
    for rank, result in enumerate(dense_results):
        text = result["text"]
        scores[text] = scores.get(text, 0.0) + 1.0 / (k + rank + 1)
        meta[text] = {
            "source": result.get("source", ""),
            "doc_type": result.get("doc_type", ""),
            "page": result.get("page", 0),
            # CAPTURE NEW STRUCTURAL HEADINGS
            "chapter": result.get("chapter", "N/A"),
            "section": result.get("section", "N/A"),
            "subsection": result.get("subsection", "N/A"),
        }

    # 2. Process sparse keyword findings 
    for rank, result in enumerate(bm25_results):
        text = result["text"]
        scores[text] = scores.get(text, 0.0) + 1.0 / (k + rank + 1)
        
        # If it wasn't found by dense, populate its metadata from the BM25 registry
        if text not in meta:
            meta[text] = {
                "source": result.get("source", ""),
                "doc_type": result.get("doc_type", ""),
                "page": result.get("page", 0),
                # CAPTURE NEW STRUCTURAL HEADINGS FROM BM25 REGISTRY
                "chapter": result.get("chapter", "N/A"),
                "section": result.get("section", "N/A"),
                "subsection": result.get("subsection", "N/A"),
            }

    # 3. Compile final fused candidates sorted descending by RRF math
    return [
        {
            "text": t,
            "rrf_score": s,
            "source": meta[t]["source"],
            "doc_type": meta[t]["doc_type"],
            "page": meta[t]["page"],
            "chapter": meta[t]["chapter"],
            "section": meta[t]["section"],
            "subsection": meta[t]["subsection"],
        }
        for t, s in sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ]