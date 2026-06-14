from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = "YOUR_GROQ_API_KEY_HERE"
    groq_model: str = "llama-3.3-70b-versatile"

    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 10
    rerank_top_n: int = 3
    bm25_pickle_path: str = "data/bm25.pkl"
    sqlite_db_path: str = "finsentinel.db"
    qdrant_collection: str = "compliance_docs"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Thresholds calibrated to match documented demo-case expected tiers:
    # Legitimate (20 pts)=LOW, Conflicting (35)=MEDIUM,
    # Structuring (40)=HIGH, Cross-border (60)=HIGH,
    # Fan-out smurfing (70)=CRITICAL
    risk_tier_low: int = 20
    risk_tier_medium: int = 39
    risk_tier_high: int = 64

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
