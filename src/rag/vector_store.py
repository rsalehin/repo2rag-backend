import os
from typing import List, Dict, Any
from langchain_core.documents import Document
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from config.settings import CHROMA_PERSIST_DIR, EMBEDDING_MODEL_NAME

COLLECTION_NAME = "repo2rag_markdown"

class DenseRetriever:
    """Manages ChromaDB collection of chunk embeddings with fast retrieval."""

    def __init__(self, persist_dir: str = None):
        self.persist_dir = persist_dir or CHROMA_PERSIST_DIR
        self.client = PersistentClient(path=self.persist_dir)
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        self.collection = None

    def ingest(self, documents: List[Document]):
        """
        Embed documents and store them in ChromaDB.
        Overwrites any existing collection with the same name.
        """
        # Delete existing collection if it exists
        try:
            self.client.delete_collection(COLLECTION_NAME)
        except:
            pass

        self.collection = self.client.create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_func,
            metadata={"hnsw:space": "cosine"}
        )

        ids = [f"chunk_{d.metadata.get('chunk_index', i)}" for i, d in enumerate(documents)]
        texts = [d.page_content for d in documents]
        metadatas = [d.metadata for d in documents]

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

    def load(self):
        """Load an existing collection."""
        self.collection = self.client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_func
        )

    def retrieve(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Return top-k dense results as list of dicts with:
        - doc: reconstructed Document
        - score: cosine similarity (0-1, higher is better)
        """
        if not self.collection:
            raise ValueError("Collection not ingested/loaded. Call ingest() or load() first.")

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        docs = []
        for i in range(len(results["documents"][0])):
            metadata = results["metadatas"][0][i] or {}
            docs.append({
                "doc": Document(
                    page_content=results["documents"][0][i],
                    metadata=metadata
                ),
                "score": 1.0 - float(results["distances"][0][i])  # convert cosine distance to similarity
            })
        return docs