from typing import List
from ..server import mcp
from mcp.server.fastmcp import Context

@mcp.tool()
def jina_deepsearch(
    ctx: Context,
    model: str,
    messages: list,
    stream: bool = None,
    reasoning_effort: str = None,
    budget_tokens: int = None,
    max_attempts: int = None,
    no_direct_answer: bool = None,
    max_returned_urls: int = None,
    response_format: dict = None,
    boost_hostnames: List[str] = None,
    bad_hostnames: List[str] = None,
    only_hostnames: List[str] = None,
) -> dict:
    """
    Combines web searching, reading, and reasoning for comprehensive investigation.
    """
    jina_client = ctx.fastmcp.jina_client
    return jina_client.call_deepsearch(
        model=model,
        messages=messages,
        stream=stream,
        reasoning_effort=reasoning_effort,
        budget_tokens=budget_tokens,
        max_attempts=max_attempts,
        no_direct_answer=no_direct_answer,
        max_returned_urls=max_returned_urls,
        response_format=response_format,
        boost_hostnames=boost_hostnames,
        bad_hostnames=bad_hostnames,
        only_hostnames=only_hostnames,
    ) 