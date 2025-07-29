from mcp.server.fastmcp import FastMCP
from .client import JinaAIAPIClient
import os

# Get your Jina AI API key for free: https://jina.ai/?sui=apikey
mcp = FastMCP("jina-ai-mcp-server")

# Get API key and create a single client instance
api_key = os.getenv("JINA_API_KEY")
if not api_key:
    # This will be a hard failure on startup if the key is not set.
    # Consider a more graceful handling if the server should start without a key.
    raise ValueError("JINA_API_KEY environment variable must be set.")

# Attach the client to the mcp server instance so it can be accessed from the context
mcp.jina_client = JinaAIAPIClient(api_key) 