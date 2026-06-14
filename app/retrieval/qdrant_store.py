# app/retrieval/qdrant_store.py
import uuid
from typing import List, Optional

from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    PointStruct,
    VectorParams,
)

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

_client: Optional[QdrantClient] = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        # Note: If deploying permanently, change ":memory:" to a local directory path like "data/qdrant_local"
        _client = QdrantClient(":memory:")
        _client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        logger.info(f"Qdrant collection '{settings.qdrant_collection}' initialised")
    return _client


def upsert_chunks(chunks: List[Document], embeddings: List[List[float]]) -> None:
    client = get_client()
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk.page_content,
                "source": chunk.metadata.get("source", ""),
                "doc_type": chunk.metadata.get("doc_type", ""),
                "page": chunk.metadata.get("page", 0),
                # NEW STRUCTURAL METADATA FIELDS
                "chapter": chunk.metadata.get("chapter", "N/A"),
                "section": chunk.metadata.get("section", "N/A"),
                "subsection": chunk.metadata.get("subsection", "N/A"),
            },
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=points)
    logger.info(f"Upserted {len(points)} chunks to Qdrant")


def dense_search(
    query_vector: List[float],
    doc_type: Optional[str] = None,
    top_k: int = 10,
) -> List[dict]:
    client = get_client()
    query_filter = None
    if doc_type:
        query_filter = Filter(
            must=[FieldCondition(key="doc_type", match=MatchAny(any=[doc_type]))]
        )
    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vector,
        limit=top_k,
        query_filter=query_filter,
        with_payload=True,
    )
    return [
        {
            "text": r.payload["text"],
            "score": r.score,
            "source": r.payload.get("source", ""),
            "doc_type": r.payload.get("doc_type", ""),
            "page": r.payload.get("page", 0),
            # NEW STRUCTURAL RETURN PAYLOADS
            "chapter": r.payload.get("chapter", "N/A"),
            "section": r.payload.get("section", "N/A"),
            "subsection": r.payload.get("subsection", "N/A"),
        }
        for r in results
    ]


def get_all_chunks() -> List[str]:
    client = get_client()
    results, _ = client.scroll(
        collection_name=settings.qdrant_collection,
        limit=10000,
        with_payload=True,
    )
    return [r.payload["text"] for r in results]


def get_collection_count() -> int:
    client = get_client()
    info = client.get_collection(settings.qdrant_collection)
    return info.points_count