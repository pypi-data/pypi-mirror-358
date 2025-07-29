from typing import List, Union
from ..server import mcp
from mcp.server.fastmcp import Context

@mcp.tool()
def jina_rerank(
    ctx: Context,
    model: str,
    query: str,
    documents: List[Union[str, dict]],
    top_n: int = None,
    return_documents: bool = None,
) -> dict:
    """
    Find the most relevant search results by refining search results or RAG contextual chunks.
    """
    jina_client = ctx.fastmcp.jina_client
    return jina_client.call_reranker(
        model=model,
        query=query,
        documents=documents,
        top_n=top_n,
        return_documents=return_documents,
    ) 