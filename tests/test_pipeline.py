"""
End‑to‑end pipeline test using a sample Markdown file.
Run: python -m tests.test_pipeline
"""
import tempfile
import os
from src.rag import RepoRAG

SAMPLE_MD = """# Test Project

## Introduction
This is a test codebase. It contains authentication logic.

## Auth Module
The auth module uses JWT tokens.
It validates tokens on every request.

## Database
The database layer is PostgreSQL.
We use connection pooling.
"""

def test_full_pipeline():
    # Write sample markdown to a temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(SAMPLE_MD)
        tmp_path = f.name

    try:
        rag = RepoRAG()
        rag.ingest(tmp_path)

        # Test retrieval
        results = rag.search("JWT tokens", final_top_k=3)
        assert len(results) > 0, "Should return at least one result"
        assert "JWT" in results[0]["doc"].page_content, "Top result should mention JWT"

        # Test citation: just ensure it's non‑empty and includes the source filename
        from src.rag.citations import format_citation
        citation = format_citation(results[0])
        assert len(citation) > 5, f"Citation too short: '{citation}'"
        assert os.path.basename(tmp_path) in citation, f"Citation should contain filename: {citation}"

        print("All assertions passed.")
    finally:
        os.unlink(tmp_path)
        # Clean up test artifacts
        import shutil
        if os.path.exists("data/chroma"):
            shutil.rmtree("data/chroma", ignore_errors=True)
        if os.path.exists("data/bm25"):
            shutil.rmtree("data/bm25", ignore_errors=True)


if __name__ == "__main__":
    test_full_pipeline()