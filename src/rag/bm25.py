import os
import pickle
from typing import List, Dict, Any
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
from config.settings import BM25_INDEX_DIR

class BM25Index:
    """Builds, persists, and queries a BM25 keyword index over chunked documents."""

    def __init__(self, index_path: str = None):
        self.index_path = index_path or os.path.join(BM25_INDEX_DIR, "bm25_index.pkl")
        self.documents: List[Document] = []
        self.bm25: BM25Okapi = None

    def build(self, documents: List[Document]):
        """Tokenize documents and build the BM25 index."""
        self.documents = documents
        tokenized = [doc.page_content.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)

    def save(self, path: str = None):
        """Persist the index and associated documents to disk."""
        target = path or self.index_path
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            pickle.dump({"documents": self.documents, "bm25": self.bm25}, f)

    def load(self, path: str = None):
        """Load a previously saved index."""
        target = path or self.index_path
        if not os.path.exists(target):
            raise FileNotFoundError(f"BM25 index not found at {target}")
        with open(target, "rb") as f:
            data = pickle.load(f)
            self.documents = data["documents"]
            self.bm25 = data["bm25"]

    def retrieve(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Return top-k results as a list of dicts with:
        - doc: the LangChain Document
        - score: BM25 score
        """
        if not self.bm25:
            raise ValueError("BM25 index not built or loaded.")
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        # Get top-k indices by score descending
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        results = []
        for idx in top_indices:
            results.append({
                "doc": self.documents[idx],
                "score": float(scores[idx])
            })
        return results