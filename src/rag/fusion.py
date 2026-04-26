from typing import List, Dict, Any
from langchain_core.documents import Document
from config.settings import RRF_K

def rrf_fuse(
    dense_results: List[Dict[str, Any]],
    bm25_results: List[Dict[str, Any]],
    k: int = RRF_K,
    final_top_k: int = None
) -> List[Dict[str, Any]]:
    """
    Fuse two ranked result lists using Reciprocal Rank Fusion.
    Each result dict must have a 'doc' key (LangChain Document) and optionally 'score'.
    Returns a merged list of dicts with keys:
        - doc: Document
        - rrf_score: combined RRF score
        - dense_rank, bm25_rank: original ranks (1-based) if present
    """
    from config.settings import FINAL_TOP_K
    if final_top_k is None:
        final_top_k = FINAL_TOP_K

    # Build lookup: doc id -> document + rank info
    doc_map = {}

    def doc_key(doc: Document) -> str:
        return f"{doc.metadata.get('source', '')}:{doc.metadata.get('chunk_index', 0)}"

    for rank, item in enumerate(dense_results, start=1):
        key = doc_key(item["doc"])
        doc_map[key] = {
            "doc": item["doc"],
            "dense_rank": rank,
            "bm25_rank": None,
            "dense_score": item.get("score", 0.0),
            "bm25_score": 0.0
        }

    for rank, item in enumerate(bm25_results, start=1):
        key = doc_key(item["doc"])
        if key in doc_map:
            doc_map[key]["bm25_rank"] = rank
            doc_map[key]["bm25_score"] = item.get("score", 0.0)
        else:
            doc_map[key] = {
                "doc": item["doc"],
                "dense_rank": None,
                "bm25_rank": rank,
                "dense_score": 0.0,
                "bm25_score": item.get("score", 0.0)
            }

    # Compute RRF scores
    fused = []
    for key, entry in doc_map.items():
        rrf = 0.0
        if entry["dense_rank"]:
            rrf += 1.0 / (k + entry["dense_rank"])
        if entry["bm25_rank"]:
            rrf += 1.0 / (k + entry["bm25_rank"])

        fused.append({
            "doc": entry["doc"],
            "rrf_score": rrf,
            "dense_rank": entry["dense_rank"],
            "bm25_rank": entry["bm25_rank"],
            "dense_score": entry["dense_score"],
            "bm25_score": entry["bm25_score"]
        })

    # Sort by RRF score descending
    fused.sort(key=lambda x: x["rrf_score"], reverse=True)
    return fused[:final_top_k]