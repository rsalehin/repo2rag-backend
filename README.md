# Repo2RAG Backend

Hybrid RAG system for Markdown codebase dumps.

## Features
- Fixed-size chunking with overlap
- BM25 keyword search + dense vector search (ChromaDB + BGE-base)
- Reciprocal Rank Fusion (RRF)
- Cross-encoder reranking
- FastAPI REST API + HTML/JS UI
- MCP server for AI agents

## Setup
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt