import os
import tempfile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.logger import get_logger
from app.ingestion.pipeline import run_ingestion_pipeline
from app.retrieval.qdrant_store import get_collection_count

logger = get_logger(__name__)
router = APIRouter()


@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        chunk_count = run_ingestion_pipeline(tmp_path, doc_type)
        collection_total = get_collection_count()
        logger.info(f"Ingested '{file.filename}': {chunk_count} chunks")
        return {
            "doc_name": file.filename,
            "chunk_count": chunk_count,
            "collection_total": collection_total,
        }
    except Exception as e:
        logger.error(f"Ingestion failed for '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)
