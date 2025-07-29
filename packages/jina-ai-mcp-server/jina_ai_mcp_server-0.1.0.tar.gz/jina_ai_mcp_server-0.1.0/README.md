# Jina AI MCP Server

This is an MCP (Model Context Protocol) server that exposes the functionalities of the Jina AI API as a set of tools.

## Features

*   **Embeddings API**: Convert text/images to fixed-length vectors.
*   **Reranker API**: Find the most relevant search results.
*   **Reader API**: Retrieve and parse content from a URL in an LLM-friendly format.
*   **Search API**: Search the web for information and return results optimized for LLMs.
*   **DeepSearch API**: Combines web searching, reading, and reasoning for comprehensive investigation.
*   **Segmenter API**: Tokenizes text and divides text into manageable chunks.
*   **Classifier API (Text)**: Perform zero-shot classification for text content.
*   **Classifier API (Image)**: Perform zero-shot classification for image content.

## Installation

This MCP server can be installed and run using `uvx` once it's published to PyPI.

## Usage

To use this MCP server, you will need to provide your Jina AI API key. This should be configured in your MCP client's `mcp.json` settings.

Example `mcp.json` configuration for this server:

```json
{
  "name": "jina-ai-mcp-server",
  "description": "MCP Server for Jina AI APIs",
  "main": "mcp_server.py",
  "mode": "local",
  "language": "python",
  "settings_schema": {
    "type": "object",
    "properties": {
      "JINA_API_KEY": {
        "type": "string",
        "description": "Your Jina AI API key. Get it for free: https://jina.ai/?sui=apikey"
      }
    },
    "required": ["JINA_API_KEY"]
  },
  "package_name": "mcp_jina_ai"
}
```

## Get your Jina AI API key for free: https://jina.ai/?sui=apikey

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.