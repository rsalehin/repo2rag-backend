import os
from dotenv import load_dotenv

load_dotenv()

# Paths
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")
BM25_INDEX_DIR = os.getenv("BM25_INDEX_DIR", "data/bm25")

# Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

# Models
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
RERANKER_MODEL_NAME = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# Retrieval
RRF_K = int(os.getenv("RRF_K", 60))
HYBRID_TOP_K = int(os.getenv("HYBRID_TOP_K", 20))
RERANK_TOP_N = int(os.getenv("RERANK_TOP_N", 10))
FINAL_TOP_K = int(os.getenv("FINAL_TOP_K", 5))