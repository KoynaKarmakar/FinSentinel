"""Phase 1 tests — ingestion and retrieval logic."""
import pytest
from app.retrieval.rrf_fusion import rrf_fuse


def _make_dense(text: str, score: float, doc_type: str = "") -> dict:
    return {"text": text, "score": score, "source": "", "doc_type": doc_type, "page": 0}


def _make_bm25(text: str, score: float, rank: int) -> dict:
    return {"text": text, "score": score, "rank": rank}


def test_rrf_fusion_returns_all_unique_docs():
    dense = [_make_dense("doc A", 0.9), _make_dense("doc B", 0.8)]
    bm25 = [_make_bm25("doc B", 15.0, 0), _make_bm25("doc C", 10.0, 1)]
    result = rrf_fuse(dense, bm25)
    texts = [r["text"] for r in result]
    assert set(texts) == {"doc A", "doc B", "doc C"}


def test_rrf_fusion_doc_in_both_lists_ranks_first():
    dense = [_make_dense("doc A", 0.9), _make_dense("doc B", 0.8)]
    bm25 = [_make_bm25("doc B", 15.0, 0), _make_bm25("doc C", 10.0, 1)]
    result = rrf_fuse(dense, bm25)
    assert result[0]["text"] == "doc B"


def test_rrf_fusion_scores_positive():
    dense = [_make_dense("chunk 1", 0.95)]
    bm25 = [_make_bm25("chunk 1", 12.0, 0)]
    result = rrf_fuse(dense, bm25)
    assert result[0]["rrf_score"] > 0


def test_rrf_fusion_empty_inputs():
    assert rrf_fuse([], []) == []


def test_rrf_fusion_only_dense():
    dense = [_make_dense("doc X", 0.9), _make_dense("doc Y", 0.7)]
    result = rrf_fuse(dense, [])
    assert len(result) == 2
    assert result[0]["text"] == "doc X"


def test_rrf_fusion_only_bm25():
    bm25 = [_make_bm25("doc P", 20.0, 0), _make_bm25("doc Q", 15.0, 1)]
    result = rrf_fuse([], bm25)
    assert len(result) == 2
    assert result[0]["text"] == "doc P"


def test_rrf_fusion_k_parameter_affects_scores():
    dense = [_make_dense("doc A", 0.9)]
    result_k60 = rrf_fuse(dense, [], k=60)
    result_k10 = rrf_fuse(dense, [], k=10)
    assert result_k10[0]["rrf_score"] > result_k60[0]["rrf_score"]


def test_rrf_fusion_preserves_metadata():
    dense = [_make_dense("doc A", 0.9, doc_type="AML")]
    result = rrf_fuse(dense, [])
    assert result[0]["doc_type"] == "AML"
