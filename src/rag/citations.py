import os
from typing import Dict, Any, List
from langchain_core.documents import Document

def _char_to_line(file_path: str, start_char: int, end_char: int) -> str:
    """
    Map character offsets to line numbers in the source file.
    Returns a string like '42-58' or '42' if start==end.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.split('\n')
    # Find line numbers for start and end characters
    line_start = 1
    line_end = 1
    count = 0
    for i, line in enumerate(lines):
        line_len = len(line) + 1  # +1 for the newline character
        if count + line_len <= start_char:
            count += line_len
            line_start = i + 2  # i+1 and then +1 for next
        else:
            line_start = i + 1
            break
    # End line
    count = 0
    for i, line in enumerate(lines):
        line_len = len(line) + 1
        if count + line_len <= end_char:
            count += line_len
            line_end = i + 2
        else:
            line_end = i + 1
            break

    line_end = max(line_start, line_end)  # safety
    if line_start == line_end:
        return str(line_start)
    return f"{line_start}-{line_end}"

def format_citation(result: Dict[str, Any]) -> str:
    """
    Build a citation string from a retrieval result dict.
    Expected keys: doc (Document) with metadata 'source', 'heading', 'start_char', 'end_char'.
    """
    doc: Document = result.get("doc")
    if not doc or not doc.metadata:
        return "[unknown source]"

    meta = doc.metadata
    source = os.path.basename(meta.get("source", "unknown"))
    heading = meta.get("heading", "")
    start = meta.get("start_char", 0)
    end = meta.get("end_char", 0)

    # Get line range
    try:
        line_range = _char_to_line(meta["source"], start, end)
    except:
        line_range = "?"

    if heading:
        return f"[{heading} ({source}:{line_range})]"
    else:
        return f"[{source}:{line_range}]"

def format_all_citations(results: List[Dict[str, Any]]) -> List[str]:
    """Return a list of citation strings for all results."""
    return [format_citation(r) for r in results]