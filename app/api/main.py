from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ingest, investigate, report
from app.core.logger import get_logger
from app.retrieval.bm25_index import load_index
from app.retrieval.qdrant_store import get_collection_count
from app.store.case_store import init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    load_index()
    logger.info("FinSentinel API ready")
    yield
    logger.info("FinSentinel API shutting down")


app = FastAPI(
    title="FinSentinel API",
    description="Agentic Financial Compliance Investigation System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])
app.include_router(investigate.router, prefix="/api", tags=["Investigation"])
app.include_router(report.router, prefix="/api", tags=["Reports"])


@app.get("/health")
def health_check():
    count = get_collection_count()
    return {"status": "ok", "service": "FinSentinel", "qdrant_chunk_count": count}
