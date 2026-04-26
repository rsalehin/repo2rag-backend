import os
from typing import List, Dict, Any
from langchain_core.documents import Document

from .chunker import load_and_chunk_markdown
from .bm25 import BM25Index
from .vector_store import DenseRetriever
from .fusion import rrf_fuse
from .reranker import Reranker
from config.settings import HYBRID_TOP_K, FINAL_TOP_K

class RepoRAG:
    """
    End-to-end RAG pipeline for a Markdown codebase dump.
    Usage:
        rag = RepoRAG()
        rag.ingest("path/to/repo.md")
        results = rag.search("How does authentication work?")
    """

    def __init__(self):
        self.documents: List[Document] = []
        self.bm25 = BM25Index()
        self.dense = DenseRetriever()
        self.reranker = Reranker()
        self._ingested = False

    def ingest(self, file_path: str, force: bool = False):
        """
        Load a Markdown file, chunk it, build BM25 index and ChromaDB collection.
        Set force=True to re-ingest even if already done.
        """
        if self._ingested and not force:
            return

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # 1. Chunk
        self.documents = load_and_chunk_markdown(file_path)

        # 2. BM25
        self.bm25.build(self.documents)

        # 3. Dense (ChromaDB)
        self.dense.ingest(self.documents)

        self._ingested = True

    def load_indices(self):
        """
        Load previously saved BM25 and ChromaDB indices from disk.
        Call this if you already ran ingest() in a previous session.
        """
        self.bm25.load()
        self.dense.load()
        self._ingested = True

    def search(
        self,
        query: str,
        hybrid_top_k: int = HYBRID_TOP_K,
        final_top_k: int = FINAL_TOP_K
    ) -> List[Dict[str, Any]]:
        """
        Run the full retrieval pipeline:
        1. BM25 retrieval (20 candidates)
        2. Dense retrieval (20 candidates)
        3. RRF fusion
        4. Cross-encoder rerank
        Returns list of dicts with keys:
            - doc: LangChain Document
            - rrf_score, rerank_score
            - dense_score, bm25_score
            - dense_rank, bm25_rank
        """
        if not self._ingested:
            raise RuntimeError("Must call ingest() or load_indices() before searching.")

        # Retrieve
        bm25_results = self.bm25.retrieve(query, top_k=hybrid_top_k)
        dense_results = self.dense.retrieve(query, top_k=hybrid_top_k)

        # Fuse
        fused = rrf_fuse(dense_results, bm25_results, final_top_k=final_top_k)

        # Rerank
        final = self.reranker.rerank(query, fused, top_k=final_top_k)
        return final