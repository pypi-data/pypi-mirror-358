from ..server import mcp
from mcp.server.fastmcp import Context

@mcp.tool()
def jina_segmenter(
    ctx: Context,
    content: str,
    tokenizer: str = "cl100k_base",
    return_tokens: bool = False,
    return_chunks: bool = False,
    max_chunk_length: int = 1000,
    head: int = None,
    tail: int = None,
) -> dict:
    """
    Tokenizes text and divides it into chunks.
    """
    jina_client = ctx.fastmcp.jina_client
    return jina_client.call_segmenter(
        content=content,
        tokenizer=tokenizer,
        return_tokens=return_tokens,
        return_chunks=return_chunks,
        max_chunk_length=max_chunk_length,
        head=head,
        tail=tail,
    ) 