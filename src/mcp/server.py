import argparse
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.rag.pipeline import RepoRAG
from src.rag.citations import format_all_citations

rag = RepoRAG()

async def serve(file_path: str):
    """Start the MCP server, ingesting the given Markdown file."""
    rag.ingest(file_path, force=True)

    server = Server("repo2rag")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="search_codebase",
                description="Search the ingested codebase Markdown. Returns relevant chunks with citations.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of top results to return (default 5, max 20)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "search_codebase":
            query = arguments["query"]
            top_k = int(arguments.get("top_k", 5))
            results = rag.search(query, final_top_k=top_k)
            citations = format_all_citations(results)

            output_lines = []
            for i, (res, cit) in enumerate(zip(results, citations), 1):
                content = res["doc"].page_content.strip()
                rerank = res.get("rerank_score", 0.0)
                output_lines.append(f"Result {i} [{cit}] (rerank={rerank:.3f}):\n{content}\n")

            return [TextContent(type="text", text="\n".join(output_lines))]
        else:
            raise ValueError(f"Unknown tool: {name}")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repo2RAG MCP Server")
    parser.add_argument("file", help="Path to Markdown file to ingest")
    args = parser.parse_args()
    asyncio.run(serve(args.file))