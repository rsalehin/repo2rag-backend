import os
import shutil
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional

from src.rag.pipeline import RepoRAG
from src.rag.citations import format_all_citations
from src.rag.llm_answer import LLMAnswerGenerator

app = FastAPI(title="Repo2RAG Backend")

# Singletons
rag = RepoRAG()
llm = LLMAnswerGenerator()

UPLOAD_DIR = "data/markdown"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class SearchResult(BaseModel):
    content: str
    citation: str
    rerank_score: float
    rrf_score: float
    dense_score: float
    bm25_score: float
    dense_rank: Optional[int] = None
    bm25_rank: Optional[int] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    answer: Optional[str] = None

@app.get("/")
async def root():
    return FileResponse("src/ui/index.html")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    if not file.filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="Only .md files are accepted")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        rag.ingest(file_path, force=True)
        return JSONResponse(content={
            "message": "Ingestion complete",
            "file": file.filename,
            "chunks": len(rag.documents)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=20)
):
    try:
        results = rag.search(q, final_top_k=top_k)
        citations = format_all_citations(results)

        items = []
        for res, cit in zip(results, citations):
            items.append(SearchResult(
                content=res["doc"].page_content,
                citation=cit,
                rerank_score=res.get("rerank_score", 0.0),
                rrf_score=res.get("rrf_score", 0.0),
                dense_score=res.get("dense_score", 0.0),
                bm25_score=res.get("bm25_score", 0.0),
                dense_rank=res.get("dense_rank"),
                bm25_rank=res.get("bm25_rank")
            ))

        # Generate LLM answer if enabled
        answer = llm.generate(q, results) if results else None

        return SearchResponse(query=q, results=items, answer=answer)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))