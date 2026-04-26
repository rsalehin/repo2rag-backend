from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
from config.settings import RERANKER_MODEL_NAME, RERANK_TOP_N

class Reranker:
    """Cross-encoder reranker for precise re-scoring of fused retrieval results."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or RERANKER_MODEL_NAME
        self.model = CrossEncoder(self.model_name)

    def rerank(
        self,
        query: str,
        fused_results: List[Dict[str, Any]],
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Re-score fused results and return top-k.
        Each fused result dict must contain a 'doc' key (LangChain Document).
        Adds a 'rerank_score' field and 'passage' text.
        """
        if top_k is None:
            from config.settings import FINAL_TOP_K
            top_k = FINAL_TOP_K

        if not fused_results:
            return []

        # Prepare (query, passage) pairs for the cross-encoder
        pairs = [(query, item["doc"].page_content) for item in fused_results]
        scores = self.model.predict(pairs)

        # Attach scores
        for item, score in zip(fused_results, scores):
            item["rerank_score"] = float(score)

        # Sort by score descending and take top_k
        reranked = sorted(fused_results, key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        return reranked[:top_k]