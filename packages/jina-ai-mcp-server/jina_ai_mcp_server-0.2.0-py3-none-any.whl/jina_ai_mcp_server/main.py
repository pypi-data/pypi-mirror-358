# main.py
from .server import mcp

# Import all tool modules to ensure the decorators run and register the tools.
# These imports might seem unused, but they are essential for the server to find the tools.
from .tools import embeddings
from .tools import reranker
from .tools import reader
from .tools import search
from .tools import deepsearch
from .tools import segmenter
from .tools import classifier_text
from .tools import classifier_image

def main():
    """
    Starts the Jina AI MCP server.

    The server is configured in `server.py` and the tools are defined in the `tools/` directory.
    This entry point imports all necessary modules and starts the FastMCP server.
    """
    print("Starting Jina AI MCP server...")
    print("Get your Jina AI API key for free: https://jina.ai/?sui=apikey")
    print("Ensure the JINA_API_KEY environment variable is set.")
    
    # The run() method starts the MCP server, listening for requests.
    # By default, it uses the STDIO transport.
    mcp.run()

if __name__ == "__main__":
    main() 