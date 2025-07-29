# Jina AI MCP Server

[![PyPI version](https://badge.fury.io/py/jina-ai-mcp-server.svg)](https://badge.fury.io/py/jina-ai-mcp-server)

This project provides a Model Context Protocol (MCP) server that exposes the Jina AI Search Foundation APIs as a suite of tools for Large Language Models (LLMs). It allows AI agents and applications to easily leverage Jina's powerful search, reranking, and content-reading capabilities.

This server is built using `mcp.py` (specifically the `FastMCP` framework) and is designed to be lightweight, fast, and easy to deploy.

## Features

The server exposes the following Jina AI APIs as MCP tools:

-   **Embeddings**: `jina_embeddings` - Convert text/images to vectors.
-   **Reranker**: `jina_rerank` - Refine search results for relevance.
-   **Reader**: `jina_reader` - Extract LLM-friendly content from URLs.
-   **Search**: `jina_search` - Perform web searches optimized for LLMs.
-   **DeepSearch**: `jina_deepsearch` - Combine search, reading, and reasoning.
-   **Segmenter**: `jina_segmenter` - Tokenize and chunk text.
-   **Text Classifier**: `jina_classify_text` - Classify text with zero-shot models.
-   **Image Classifier**: `jina_classify_image` - Classify images with zero-shot models.

## ⚙️ Configuration

Before running the server, you must obtain a Jina AI API key and set it as an environment variable.

1.  **Get your API Key**: You can get a free API key from [jina.ai](https://jina.ai/?sui=apikey).
2.  **Set the Environment Variable**:
    ```bash
    export JINA_API_KEY="your_api_key_here"
    ```
    The server will fail to start if this variable is not set.

## 🚀 Running the Server

There are multiple ways to run the Jina AI MCP server, depending on your environment and preferences.

### Using `uvx` (Recommended)

If you have `uv` installed, you can run the server directly from PyPI without cloning the repository using `uvx`. This is the quickest way to get started.

```bash
# Ensure JINA_API_KEY is set first
uvx jina-ai-mcp-server
```

This command will download the package into a temporary virtual environment and execute its entry point (`main.py`).

### Using Docker

A Dockerfile is provided for containerized deployments. This is the recommended approach for production or isolated environments.

1.  **Build the Docker Image**:
    From the root of the project directory, run:
    ```bash
    docker build -t jina-ai-mcp-server .
    ```

2.  **Run the Docker Container**:
    You must pass the `JINA_API_KEY` environment variable to the container.
    ```bash
    docker run -e JINA_API_KEY="your_api_key_here" --rm -it jina-ai-mcp-server
    ```
    The server will start inside the container.

### From Source

If you have cloned the repository, you can run it locally.

1.  **Install Dependencies**:
    It's recommended to use a virtual environment.
    ```bash
    # Using uv
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt # Or install from pyproject.toml

    # Using standard pip/venv
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    ```

2.  **Run the Server**:
    ```bash
    # Ensure JINA_API_KEY is set first
    python main.py
    ```

## 🔌 Connecting with MCP Clients

To use this server with an MCP client (like the Claude extension), you need to add its configuration to your `mcpServers.json` file. You can choose the execution method that best suits your setup.

### With `uvx` (Recommended)

This method runs the server directly from PyPI without needing Docker or a local checkout.

```json
{
  "mcpServers": {
    "jina-ai": {
      "command": "uvx",
      "args": [
        "jina-ai-mcp-server"
      ],
      "env": {
        "JINA_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### With Docker

This method requires you to have built the Docker image first (`docker build -t jina-ai-mcp-server .`).

```json
{
  "mcpServers": {
    "jina-ai": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "jina-ai-mcp-server"
      ],
      "env": {
        "JINA_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## 📦 Publishing (For Developers)

To publish a new version to PyPI:

1.  **Install build tools**:
    ```bash
    pip install build twine
    ```
2.  **Build the package**:
    ```bash
    python -m build
    ```
3.  **Upload to PyPI**:
    ```bash
    twine upload dist/*
    ``` 