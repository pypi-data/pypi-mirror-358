from typing import List, Union
from ..server import mcp
from mcp.server.fastmcp import Context

@mcp.tool()
def jina_embeddings(
    ctx: Context,
    model: str,
    input_data: List[Union[str, dict]],
    embedding_type: str = None,
    task: str = None,
    dimensions: int = None,
    normalized: bool = None,
    late_chunking: bool = None,
    truncate: bool = None,
) -> dict:
    """
    Convert text/images to fixed-length vectors for semantic search, similarity matching, clustering, etc.
    """
    jina_client = ctx.fastmcp.jina_client
    return jina_client.call_embeddings(
        model=model,
        input_data=input_data,
        embedding_type=embedding_type,
        task=task,
        dimensions=dimensions,
        normalized=normalized,
        late_chunking=late_chunking,
        truncate=truncate,
    ) 