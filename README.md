# Repo2RAG Backend

**AI-optimized codebase Q&A for Markdown repository dumps.**

Repo2RAG Backend turns a Markdown dump of a codebase into a local hybrid RAG system with keyword search, dense retrieval, reciprocal rank fusion, cross-encoder reranking, citations, a FastAPI API, a lightweight web UI, and an optional MCP server for AI coding agents.

It is designed for cases where you have already converted a GitHub repository into a single Markdown file using a tool such as `repo2rag`, `repomix`, `gitingest`, or a custom repository exporter.

---

## What it does

Given a Markdown file representing a codebase, Repo2RAG Backend builds a searchable local index and answers questions such as:

- "How does authentication work?"
- "Where is the database session created?"
- "Which files implement the agent loop?"
- "Explain the retrieval pipeline."
- "What calls the reranker?"
- "Where should I modify the API endpoint?"
- "Which chunks are relevant to this bug?"

The system combines:

- **BM25 keyword retrieval** for exact identifiers, filenames, symbols, API routes, and configuration names.
- **Dense vector retrieval** for semantic/conceptual matches.
- **Reciprocal Rank Fusion (RRF)** to merge lexical and semantic results.
- **Cross-encoder reranking** to improve final result precision.
- **Citations** with source file path, heading, chunk ID, and line information when available.
- **Optional LLM answer generation** using Claude, with retrieved evidence as context.
- **FastAPI REST API** for integration.
- **HTML/JavaScript UI** for local interaction.
- **MCP server** so tools such as Claude Desktop, Claude Code, Cursor, or other MCP-compatible agents can query the indexed codebase.

---

## Why this project exists

Vector-only RAG is usually weak for codebases.

Repository questions often contain exact identifiers:

```text
AuthMiddleware
src/api/server.py
validate_token()
ANTHROPIC_API_KEY
/ingest
RepoRAG.search()
```

A dense embedding model may understand the general meaning but miss exact names. BM25 is strong for exact terms, while dense retrieval is strong for conceptual questions. This project combines both, then reranks the merged candidates.

The intended retrieval flow is:

```text
Markdown repository dump
        |
        v
Markdown-aware chunking
        |
        +-------------------------+
        |                         |
        v                         v
BM25 keyword index          ChromaDB vector index
(rank-bm25)                BAAI/bge-base-en-v1.5
        |                         |
        +------------+------------+
                     |
                     v
        Reciprocal Rank Fusion
                 RRF(k=60)
                     |
                     v
        Cross-encoder reranking
  cross-encoder/ms-marco-MiniLM-L6-v2
                     |
                     v
        Cited search results / LLM answer
                     |
                     v
FastAPI API + Web UI + MCP Server
```

---

## Core features

### Retrieval

- Fixed-size chunking with configurable overlap.
- BM25 keyword search using `rank-bm25`.
- Dense vector search using ChromaDB.
- Default embedding model: `BAAI/bge-base-en-v1.5`.
- Reciprocal Rank Fusion with configurable `RRF_K`.
- Cross-encoder reranking using `cross-encoder/ms-marco-MiniLM-L6-v2`.
- Configurable candidate counts and final result count.

### Codebase-oriented citations

Each result can include:

- source path
- heading
- chunk ID
- score
- retrieval source
- reranker score
- line range, if recoverable from the Markdown dump

Example citation object:

```json
{
  "chunk_id": "chunk_0042",
  "source_path": "src/rag/pipeline.py",
  "heading": "RepoRAG.search",
  "line_start": 120,
  "line_end": 168,
  "score": 0.891
}
```

### API and UI

- FastAPI REST API.
- Automatic OpenAPI documentation at `/docs`.
- Minimal local HTML/JavaScript UI.
- Drag-and-drop Markdown ingestion.
- Search endpoint returning ranked chunks and citations.
- Optional answer-generation endpoint.

### Agent integration

- MCP server for agent workflows.
- Exposes repository search as a tool.
- Designed for local AI coding assistants that need precise, cited context from a codebase.

---

## Tech stack

| Layer | Technology |
|---|---|
| API | FastAPI, Uvicorn |
| Keyword retrieval | rank-bm25 |
| Vector database | ChromaDB |
| Embeddings | sentence-transformers, `BAAI/bge-base-en-v1.5` |
| Reranking | sentence-transformers CrossEncoder, `cross-encoder/ms-marco-MiniLM-L6-v2` |
| Fusion | Reciprocal Rank Fusion |
| Optional LLM | Anthropic Claude API |
| MCP integration | Model Context Protocol Python server |
| UI | Static HTML, CSS, JavaScript |
| Config | `.env`, Pydantic settings |
| Testing | pytest |

---

## Project status

This project is intended as a production-style backend foundation. The first version is deliberately simple:

- one Markdown file per index
- local persistence
- local retrieval
- optional cloud LLM only for final answer generation

Recommended future improvements are listed in the [Roadmap](#roadmap).

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/repo2rag-backend.git
cd repo2rag-backend
```

### 2. Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

#### Windows CMD

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### macOS/Linux

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create environment file

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` as needed.

---

## Configuration

All major settings live in `.env`.

| Variable | Default | Description |
|---|---:|---|
| `CHUNK_SIZE` | `1000` | Maximum chunk size in characters. |
| `CHUNK_OVERLAP` | `200` | Character overlap between adjacent chunks. |
| `EMBEDDING_MODEL` | `BAAI/bge-base-en-v1.5` | Sentence-transformer embedding model. |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L6-v2` | Cross-encoder used for reranking. |
| `RRF_K` | `60` | Reciprocal Rank Fusion constant. |
| `HYBRID_TOP_K` | `20` | Number of candidates retrieved from each retriever before fusion. |
| `FINAL_TOP_K` | `5` | Number of final reranked results returned. |
| `CHROMA_DIR` | `data/chroma` | ChromaDB persistence directory. |
| `BM25_DIR` | `data/bm25` | BM25 persistence directory. |
| `MARKDOWN_DIR` | `data/markdown` | Uploaded Markdown storage directory. |
| `LLM_ENABLED` | `false` | Enables optional Claude answer generation. |
| `ANTHROPIC_API_KEY` | empty | Required only if `LLM_ENABLED=true`. |
| `ANTHROPIC_MODEL` | `claude-3-5-sonnet-latest` | Claude model for final answer generation. |
| `API_HOST` | `127.0.0.1` | FastAPI host. |
| `API_PORT` | `8000` | FastAPI port. |

Example `.env`:

```env
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L6-v2

RRF_K=60
HYBRID_TOP_K=20
FINAL_TOP_K=5

CHROMA_DIR=data/chroma
BM25_DIR=data/bm25
MARKDOWN_DIR=data/markdown

LLM_ENABLED=false
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-latest

API_HOST=127.0.0.1
API_PORT=8000
```

---

## Usage

### 1. Start the API server

```bash
uvicorn src.api.server:app --reload --host 127.0.0.1 --port 8000
```

### 2. Open the web UI

Visit:

```text
http://127.0.0.1:8000/
```

### 3. Open the API docs

Visit:

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically exposes Swagger/OpenAPI documentation at this endpoint.

---

## Ingest a Markdown codebase dump

### Option A: Web UI

Open the UI and drag a `.md` file into the upload area.

### Option B: API

```bash
curl -X POST \
  -F "file=@repo_dump.md" \
  http://127.0.0.1:8000/ingest
```

Example response:

```json
{
  "status": "ok",
  "document_id": "repo_dump",
  "chunks": 248,
  "bm25_indexed": true,
  "vector_indexed": true
}
```

---

## Search

### Web UI

Type a question into the search box.

Example:

```text
How does authentication work?
```

### API

```bash
curl "http://127.0.0.1:8000/search?q=How+does+authentication+work%3F&top_k=5"
```

Example response:

```json
{
  "query": "How does authentication work?",
  "results": [
    {
      "rank": 1,
      "chunk_id": "chunk_0031",
      "source_path": "src/auth/middleware.py",
      "heading": "AuthMiddleware",
      "line_start": 42,
      "line_end": 91,
      "score": 0.912,
      "text": "..."
    }
  ]
}
```

---

## Generate an answer with citations

If `LLM_ENABLED=true`, the system can generate a final natural-language answer using retrieved chunks as evidence.

```bash
curl "http://127.0.0.1:8000/answer?q=Explain+the+retrieval+pipeline"
```

Example response:

```json
{
  "query": "Explain the retrieval pipeline",
  "answer": "The retrieval pipeline first chunks the Markdown dump, then builds both BM25 and ChromaDB indexes...",
  "citations": [
    {
      "source_path": "src/rag/pipeline.py",
      "heading": "RepoRAG.search",
      "line_start": 88,
      "line_end": 140
    }
  ]
}
```

---

## MCP server usage

The MCP server exposes Repo2RAG search to AI agents.

### Example Claude Desktop configuration

Add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "repo2rag": {
      "command": "python",
      "args": [
        "src/mcp/server.py",
        "path/to/repo_dump.md"
      ]
    }
  }
}
```

### Suggested MCP tools

The MCP server should expose tools like:

| Tool | Purpose |
|---|---|
| `ingest_markdown` | Index a Markdown repository dump. |
| `search_codebase` | Search the codebase with hybrid retrieval and reranking. |
| `get_chunk` | Retrieve a specific chunk by ID. |
| `list_sources` | List indexed source files/headings. |
| `answer_question` | Generate a cited answer using retrieved context. |

Example tool schema:

```json
{
  "name": "search_codebase",
  "description": "Search the indexed repository dump using hybrid retrieval and cross-encoder reranking.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The user question or search query."
      },
      "top_k": {
        "type": "integer",
        "default": 5,
        "description": "Number of final reranked results."
      }
    },
    "required": ["query"]
  }
}
```

---

## Recommended Markdown input format

The system works best when the repository dump preserves file boundaries.

Recommended format:

````markdown
# Repository: example-project

## File: src/api/server.py

```python
from fastapi import FastAPI

app = FastAPI()
```

## File: src/rag/pipeline.py

```python
class RepoRAG:
    ...
```
````

Better metadata produces better citations.

Recommended metadata per file:

```markdown
## File: src/rag/pipeline.py
Language: python
Lines: 1-240
```

If your exporter can preserve line numbers, include them.

---

## Project structure

```text
repo2rag-backend/
├── config/
│   ├── __init__.py
│   └── settings.py              # Environment and runtime settings
├── src/
│   ├── __init__.py
│   ├── main.py                  # Optional CLI entrypoint
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── chunker.py           # Markdown -> chunks/documents
│   │   ├── bm25.py              # BM25 index and retrieval
│   │   ├── vector_store.py      # ChromaDB dense retrieval
│   │   ├── fusion.py            # Reciprocal Rank Fusion
│   │   ├── reranker.py          # Cross-encoder reranking
│   │   ├── pipeline.py          # Unified RepoRAG pipeline
│   │   ├── citations.py         # Citation formatting
│   │   └── llm_answer.py        # Optional LLM answer generation
│   ├── api/
│   │   ├── __init__.py
│   │   └── server.py            # FastAPI app and endpoints
│   ├── ui/
│   │   └── index.html           # Local demo UI
│   └── mcp/
│       ├── __init__.py
│       └── server.py            # MCP server
├── tests/
│   ├── test_chunker.py
│   ├── test_bm25.py
│   ├── test_fusion.py
│   ├── test_reranker.py
│   └── test_pipeline.py
├── data/
│   ├── chroma/                  # ChromaDB persistence
│   ├── bm25/                    # BM25 persistence
│   └── markdown/                # Uploaded Markdown files
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## API reference

### `POST /ingest`

Indexes a Markdown file.

Request:

```bash
curl -X POST \
  -F "file=@repo_dump.md" \
  http://127.0.0.1:8000/ingest
```

Response:

```json
{
  "status": "ok",
  "document_id": "repo_dump",
  "chunks": 248
}
```

### `GET /search`

Runs hybrid retrieval and reranking.

Request:

```bash
curl "http://127.0.0.1:8000/search?q=How+does+the+agent+work%3F&top_k=5"
```

Query parameters:

| Parameter | Type | Default | Description |
|---|---:|---:|---|
| `q` | string | required | Search query. |
| `top_k` | integer | `5` | Number of final results. |

### `GET /answer`

Generates an optional LLM answer with citations.

Request:

```bash
curl "http://127.0.0.1:8000/answer?q=Explain+the+architecture"
```

Requires:

```env
LLM_ENABLED=true
ANTHROPIC_API_KEY=your_api_key_here
```

### `GET /health`

Health check endpoint.

Response:

```json
{
  "status": "ok"
}
```

---

## Retrieval pipeline details

### 1. Chunking

The first version uses fixed-size overlapping chunks:

```text
chunk size: 1000 characters
overlap:    200 characters
```

This is simple and reliable, but not perfect for code. See the roadmap for Markdown-aware and AST-aware chunking improvements.

### 2. BM25 retrieval

BM25 is used for exact lexical matching.

Good for:

- function names
- class names
- file paths
- route names
- environment variables
- config keys
- error messages
- CLI commands

### 3. Dense retrieval

Dense retrieval uses sentence-transformer embeddings and ChromaDB.

Good for:

- conceptual questions
- architecture questions
- "where is this idea implemented?"
- "how does this subsystem work?"

### 4. Reciprocal Rank Fusion

RRF combines ranked results from BM25 and dense retrieval.

A document that ranks well in both systems usually moves higher.

Simplified formula:

```text
score(d) = Σ 1 / (k + rank_i(d))
```

Default:

```text
k = 60
```

### 5. Cross-encoder reranking

The cross-encoder receives `(query, chunk)` pairs and scores them directly.

This is slower than embedding search, but usually more precise for the final top candidates.

Recommended pattern:

```text
BM25 top 20
+ dense top 20
→ RRF fusion
→ top 20 candidates
→ cross-encoder reranking
→ final top 5
```

---

## Development

### Run tests

```bash
pytest
```

### Run with auto-reload

```bash
uvicorn src.api.server:app --reload
```

### Suggested development dependencies

```text
pytest
pytest-cov
ruff
mypy
pre-commit
```

### Suggested quality commands

```bash
ruff check .
mypy src
pytest --cov=src
```

---

## Security notes

- Do not expose the local API publicly without authentication.
- Do not upload private repository dumps to remote services unless you trust the environment.
- If LLM answer generation is enabled, retrieved chunks may be sent to the configured LLM provider.
- Keep MCP server access local unless you implement authentication and allow-listed tools.
- Treat Markdown dumps from untrusted repositories as untrusted input.
- Avoid executing code from ingested repositories.

---

## Limitations

Current design limitations:

- Fixed-size chunking can split functions or classes awkwardly.
- A single Markdown dump loses some repository structure unless the exporter preserves metadata.
- Cross-encoder reranking can be slow on CPU for large candidate sets.
- ChromaDB and BM25 indexes must be kept in sync.
- LLM-generated answers can still be wrong if retrieval misses key context.
- Line numbers depend on the quality of the original Markdown export.

---

## Roadmap

### Retrieval quality

- Markdown-aware chunking by heading and file section.
- Code-aware chunking by functions/classes when line metadata exists.
- AST-assisted chunk metadata for Python/TypeScript/JavaScript.
- Query rewriting for codebase questions.
- Multi-stage reranking.
- Hybrid search weighting by query type.
- Deduplication of near-identical chunks.

### Developer workflow

- CLI command:

```bash
repo2rag ingest repo_dump.md
repo2rag search "How does auth work?"
repo2rag serve
repo2rag mcp
```

- GitHub Action integration.
- Docker support.
- Persistent multi-project indexes.
- Import from `repomix`, `gitingest`, and raw GitHub URLs.
- Export search results as Markdown reports.

### Agent workflow

- Better MCP tools.
- Tool for "explain file."
- Tool for "trace symbol."
- Tool for "summarize subsystem."
- Tool for "find likely files to edit."
- Tool for "generate implementation plan from retrieved evidence."

### Evaluation

- Add benchmark queries.
- Track retrieval recall.
- Track reranker precision.
- Add golden-answer tests.
- Add citation correctness tests.

---

## Example end-to-end flow

```bash
# 1. Start server
uvicorn src.api.server:app --reload --host 127.0.0.1 --port 8000

# 2. Ingest Markdown dump
curl -X POST -F "file=@repo_dump.md" http://127.0.0.1:8000/ingest

# 3. Search
curl "http://127.0.0.1:8000/search?q=How+does+retrieval+work%3F&top_k=5"

# 4. Generate answer, if LLM is enabled
curl "http://127.0.0.1:8000/answer?q=Explain+the+retrieval+pipeline"
```

---

## Minimal `requirements.txt`

A starting dependency file could look like this:

```text
fastapi
uvicorn[standard]
python-multipart
pydantic
pydantic-settings
python-dotenv

rank-bm25
chromadb
sentence-transformers
torch

anthropic
mcp

numpy
scikit-learn

pytest
ruff
```

Pin exact versions before production use.

---

## License

Choose a license before publishing.

Recommended options:

- MIT for maximum reuse.
- Apache-2.0 for stronger patent language.
- AGPL-3.0 if you want network-use source-sharing obligations.

---

## Acknowledgements

This project builds on common retrieval patterns used in modern RAG systems:

- lexical retrieval with BM25
- dense retrieval with sentence-transformer embeddings
- reciprocal rank fusion
- cross-encoder reranking
- local vector storage
- cited answer generation
- Model Context Protocol integration for AI agents
