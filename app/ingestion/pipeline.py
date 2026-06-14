from app.core.logger import get_logger
from app.ingestion.chunker import chunk_documents
from app.ingestion.embedder import embed_chunks
from app.ingestion.loader import load_pdf
from app.retrieval.bm25_index import build_and_save_index
from app.retrieval.qdrant_store import upsert_chunks

logger = get_logger(__name__)


def run_ingestion_pipeline(file_path: str, doc_type: str) -> int:
    documents = load_pdf(file_path, doc_type)
    chunks = chunk_documents(documents)
    embeddings = embed_chunks(chunks)
    upsert_chunks(chunks, embeddings)
    build_and_save_index()
    logger.info(f"Pipeline complete: {len(chunks)} chunks from {file_path}")
    return len(chunks)
