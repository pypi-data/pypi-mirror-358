from typing import List, Dict
from ..server import mcp
from mcp.server.fastmcp import Context

@mcp.tool()
def jina_classify_image(
    ctx: Context,
    input_data: List[Dict[str, str]],
    labels: List[str],
    model: str = "jina-clip-v2",
) -> dict:
    """
    Classify images into categories using a zero-shot model. 
    Each item in input_data should be a dict like: {"image": "base64_image_string"}.
    """
    jina_client = ctx.fastmcp.jina_client
    return jina_client.call_classifier(
        model=model,
        input_data=input_data,
        labels=labels
    ) 