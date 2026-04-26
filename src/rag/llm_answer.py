from typing import List, Dict, Any
import anthropic
from config.settings import (
    LLM_ENABLED,
    ANTHROPIC_API_KEY,
    LLM_MODEL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    FINAL_TOP_K
)

class LLMAnswerGenerator:
    """Generates a synthesized answer from retrieval results using Claude API."""

    def __init__(self):
        self.enabled = LLM_ENABLED and ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "your-api-key-here"
        self.client = None
        if self.enabled:
            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate(self, query: str, results: List[Dict[str, Any]]) -> str:
        """
        Build a prompt from the retrieved chunks and call Claude.
        Returns a generated answer with inline citations, or an empty string if disabled.
        """
        if not self.enabled:
            return ""

        # Prepare context snippets
        context_parts = []
        for i, res in enumerate(results, 1):
            doc = res["doc"]
            heading = doc.metadata.get("heading", "")
            source = doc.metadata.get("source", "unknown")
            content = doc.page_content.strip()
            snippet = f"--- Document {i} ---\n" \
                      f"Source: {source}\n" \
                      f"Heading: {heading}\n" \
                      f"Content:\n{content}\n"
            context_parts.append(snippet)

        context = "\n".join(context_parts)

        system_prompt = (
            "You are an AI assistant helping a developer understand a codebase. "
            "Answer the user's question based **only** on the provided codebase snippets. "
            "When you refer to information from a snippet, cite it using its Document number in brackets, e.g. [1]. "
            "If the answer cannot be derived from the snippets, say so honestly. "
            "Be concise and code‑aware."
        )

        user_message = f"Question:\n{query}\n\nCodebase snippets:\n{context}"

        try:
            response = self.client.messages.create(
                model=LLM_MODEL,
                max_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text
        except Exception as e:
            return f"(LLM error: {e})"