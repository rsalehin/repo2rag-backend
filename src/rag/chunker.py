from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
import os
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

def extract_heading_context(text: str, max_heading_length: int = 80) -> str:
    """
    Find the first markdown heading in the chunk text.
    Returns the heading line if found, otherwise empty string.
    """
    heading_pattern = r'^(#{1,6}\s+.+)$'
    lines = text.split('\n')
    for line in lines:
        match = re.match(heading_pattern, line.strip())
        if match:
            heading = match.group(1).strip()
            if len(heading) > max_heading_length:
                heading = heading[:max_heading_length] + '...'
            return heading
    return ''

def load_and_chunk_markdown(
    file_path: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> list[Document]:
    """
    Load a Markdown file and split it into overlapping chunks.
    Each chunk is a LangChain Document with metadata:
        - source: file path
        - chunk_index: integer index
        - heading: nearest section heading (if found)
        - start_char, end_char: estimated character offsets
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        full_text = f.read()

    # Markdown-aware separators: try to respect headings and code fences
    separators = [
        "\n## ",
        "\n### ",
        "\n#### ",
        "\n##### ",
        "\n###### ",
        "\n```\n",
        "\n\n",
        "\n",
        " ",
        ""
    ]

    splitter = RecursiveCharacterTextSplitter(
        separators=separators,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = splitter.split_text(full_text)

    documents = []
    current_offset = 0
    for i, chunk in enumerate(chunks):
        start = current_offset
        end = start + len(chunk)
        current_offset = end - chunk_overlap if chunk_overlap < len(chunk) else end

        heading = extract_heading_context(chunk)

        doc = Document(
            page_content=chunk,
            metadata={
                "source": file_path,
                "chunk_index": i,
                "heading": heading,
                "start_char": start,
                "end_char": end,
            }
        )
        documents.append(doc)

    return documents