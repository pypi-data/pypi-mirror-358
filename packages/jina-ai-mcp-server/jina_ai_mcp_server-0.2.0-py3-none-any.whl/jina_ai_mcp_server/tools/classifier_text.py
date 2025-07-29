from typing import List
from ..server import mcp
from mcp.server.fastmcp import Context

@mcp.tool()
def jina_classify_text(
    ctx: Context,
    input_data: List[str],
    labels: List[str],
    model: str = "jina-embeddings-v3",
) -> dict:
    """
    Classify text into categories using a zero-shot model.
    """
    jina_client = ctx.fastmcp.jina_client
    return jina_client.call_classifier(
        model=model,
        input_data=input_data,
        labels=labels
    ) 