from ..server import mcp
from mcp.server.fastmcp import Context

@mcp.tool()
def jina_search(
    ctx: Context,
    q: str,
    gl: str = None,
    location: str = None,
    hl: str = None,
    num: int = None,
    page: int = None,
    x_site: str = None,
    x_with_links_summary: str = None,
    x_with_images_summary: str = None,
    x_retain_images: str = None,
    x_no_cache: bool = None,
    x_with_generated_alt: bool = None,
    x_respond_with: str = None,
    x_with_favicon: bool = None,
    x_return_format: str = None,
    x_engine: str = None,
    x_with_favicons: bool = None,
    x_timeout: int = None,
    x_set_cookie: str = None,
    x_proxy_url: str = None,
    x_locale: str = None,
) -> dict:
    """
    Search the web for information and return results optimized for LLMs.
    """
    jina_client = ctx.fastmcp.jina_client
    return jina_client.call_search(
        q=q,
        gl=gl,
        location=location,
        hl=hl,
        num=num,
        page=page,
        x_site=x_site,
        x_with_links_summary=x_with_links_summary,
        x_with_images_summary=x_with_images_summary,
        x_retain_images=x_retain_images,
        x_no_cache=x_no_cache,
        x_with_generated_alt=x_with_generated_alt,
        x_respond_with=x_respond_with,
        x_with_favicon=x_with_favicon,
        x_return_format=x_return_format,
        x_engine=x_engine,
        x_with_favicons=x_with_favicons,
        x_timeout=x_timeout,
        x_set_cookie=x_set_cookie,
        x_proxy_url=x_proxy_url,
        x_locale=x_locale,
    ) 