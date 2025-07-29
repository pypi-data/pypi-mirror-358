import os
import requests
import json
import time

# Get your Jina AI API key for free: https://jina.ai/?sui=apikey

class JinaAIAPIClient:
    """
    A client for interacting with the Jina AI API.
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Jina AI API key cannot be empty.")
        self._api_key = api_key
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, url: str, json_data: dict = None, custom_headers: dict = None):
        """
        Makes an HTTP request to the Jina AI API with retry logic.
        """
        headers = self._headers.copy()
        if custom_headers:
            headers.update(custom_headers)

        retries = 3
        for attempt in range(retries):
            try:
                response = requests.request(method, url, headers=headers, json=json_data)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                return response.json()
            except requests.exceptions.HTTPError as e:
                print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
                if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    # Client error (except rate limit), no need to retry
                    raise
                if attempt < retries - 1:
                    print(f"Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                else:
                    raise
            except requests.exceptions.ConnectionError as e:
                print(f"Connection Error: {e}")
                if attempt < retries - 1:
                    print(f"Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                else:
                    raise
            except requests.exceptions.Timeout as e:
                print(f"Timeout Error: {e}")
                if attempt < retries - 1:
                    print(f"Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                else:
                    raise
            except requests.exceptions.RequestException as e:
                print(f"Request Exception: {e}")
                raise

    # Jina AI API methods will be implemented here
    # 1. Embeddings API
    def call_embeddings(self, model: str, input_data: list, embedding_type: str = None,
                        task: str = None, dimensions: int = None, normalized: bool = None,
                        late_chunking: bool = None, truncate: bool = None):
        url = "https://api.jina.ai/v1/embeddings"
        payload = {
            "model": model,
            "input": input_data
        }
        if embedding_type is not None:
            payload["embedding_type"] = embedding_type
        if task is not None:
            payload["task"] = task
        if dimensions is not None:
            payload["dimensions"] = dimensions
        if normalized is not None:
            payload["normalized"] = normalized
        if late_chunking is not None:
            payload["late_chunking"] = late_chunking
        if truncate is not None:
            payload["truncate"] = truncate
        return self._make_request("POST", url, json_data=payload)

    # 2. Reranker API
    def call_reranker(self, model: str, query, documents: list, top_n: int = None, return_documents: bool = None):
        url = "https://jina.ai/v1/rerank" # The documentation has this as 'api.jina.ai/v1/rerank', fixing it here.
        payload = {
            "model": model,
            "query": query,
            "documents": documents
        }
        if top_n is not None:
            payload["top_n"] = top_n
        if return_documents is not None:
            payload["return_documents"] = return_documents
        return self._make_request("POST", url, json_data=payload)

    # 3. Reader API
    def call_reader(self, url: str, viewport: dict = None, inject_page_script: str = None,
                    x_engine: str = None, x_timeout: int = None, x_target_selector: str = None,
                    x_wait_for_selector: str = None, x_remove_selector: str = None,
                    x_with_links_summary: str = None, x_with_images_summary: str = None,
                    x_with_generated_alt: bool = None, x_no_cache: bool = None,
                    x_with_iframe: bool = None, x_return_format: str = None,
                    x_token_budget: int = None, x_retain_images: str = None,
                    x_respond_with: str = None, x_set_cookie: str = None,
                    x_proxy_url: str = None, x_proxy: str = None, dnt: int = None,
                    x_no_gfm: bool = None, x_locale: str = None, x_robots_txt: str = None,
                    x_with_shadow_dom: bool = None, x_base: str = None,
                    x_md_heading_style: str = None, x_md_hr: str = None,
                    x_md_bullet_list_marker: str = None, x_md_em_delimiter: str = None,
                    x_md_strong_delimiter: str = None, x_md_link_style: str = None,
                    x_md_link_reference_style: str = None):
        api_url = "https://r.jina.ai/"
        payload = {"url": url}
        if viewport:
            payload["viewport"] = viewport
        if inject_page_script:
            payload["injectPageScript"] = inject_page_script

        custom_headers = {}
        if x_engine: custom_headers["X-Engine"] = x_engine
        if x_timeout is not None: custom_headers["X-Timeout"] = str(x_timeout)
        if x_target_selector: custom_headers["X-Target-Selector"] = x_target_selector
        if x_wait_for_selector: custom_headers["X-Wait-For-Selector"] = x_wait_for_selector
        if x_remove_selector: custom_headers["X-Remove-Selector"] = x_remove_selector
        if x_with_links_summary: custom_headers["X-With-Links-Summary"] = x_with_links_summary
        if x_with_images_summary: custom_headers["X-With-Images-Summary"] = x_with_images_summary
        if x_with_generated_alt is not None: custom_headers["X-With-Generated-Alt"] = str(x_with_generated_alt).lower()
        if x_no_cache is not None: custom_headers["X-No-Cache"] = str(x_no_cache).lower()
        if x_with_iframe is not None: custom_headers["X-With-Iframe"] = str(x_with_iframe).lower()
        if x_return_format: custom_headers["X-Return-Format"] = x_return_format
        if x_token_budget is not None: custom_headers["X-Token-Budget"] = str(x_token_budget)
        if x_retain_images: custom_headers["X-Retain-Images"] = x_retain_images
        if x_respond_with: custom_headers["X-Respond-With"] = x_respond_with
        if x_set_cookie: custom_headers["X-Set-Cookie"] = x_set_cookie
        if x_proxy_url: custom_headers["X-Proxy-Url"] = x_proxy_url
        if x_proxy: custom_headers["X-Proxy"] = x_proxy
        if dnt is not None: custom_headers["DNT"] = str(dnt)
        if x_no_gfm is not None: custom_headers["X-No-Gfm"] = str(x_no_gfm).lower()
        if x_locale: custom_headers["X-Locale"] = x_locale
        if x_robots_txt: custom_headers["X-Robots-Txt"] = x_robots_txt
        if x_with_shadow_dom is not None: custom_headers["X-With-Shadow-Dom"] = str(x_with_shadow_dom).lower()
        if x_base: custom_headers["X-Base"] = x_base
        if x_md_heading_style: custom_headers["X-Md-Heading-Style"] = x_md_heading_style
        if x_md_hr: custom_headers["X-Md-Hr"] = x_md_hr
        if x_md_bullet_list_marker: custom_headers["X-Md-Bullet-List-Marker"] = x_md_bullet_list_marker
        if x_md_em_delimiter: custom_headers["X-Md-Em-Delimiter"] = x_md_em_delimiter
        if x_md_strong_delimiter: custom_headers["X-Md-Strong-Delimiter"] = x_md_strong_delimiter
        if x_md_link_style: custom_headers["X-Md-Link-Style"] = x_md_link_style
        if x_md_link_reference_style: custom_headers["X-Md-Link-Reference-Style"] = x_md_link_reference_style

        return self._make_request("POST", api_url, json_data=payload, custom_headers=custom_headers)

    # 4. Search API
    def call_search(self, q: str, gl: str = None, location: str = None, hl: str = None,
                    num: int = None, page: int = None, x_site: str = None,
                    x_with_links_summary: str = None, x_with_images_summary: str = None,
                    x_retain_images: str = None, x_no_cache: bool = None,
                    x_with_generated_alt: bool = None, x_respond_with: str = None,
                    x_with_favicon: bool = None, x_return_format: str = None,
                    x_engine: str = None, x_with_favicons: bool = None,
                    x_timeout: int = None, x_set_cookie: str = None,
                    x_proxy_url: str = None, x_locale: str = None):
        api_url = "https://s.jina.ai/"
        payload = {"q": q}
        if gl: payload["gl"] = gl
        if location: payload["location"] = location
        if hl: payload["hl"] = hl
        if num is not None: payload["num"] = num
        if page is not None: payload["page"] = page

        custom_headers = {}
        if x_site: custom_headers["X-Site"] = x_site
        if x_with_links_summary: custom_headers["X-With-Links-Summary"] = x_with_links_summary
        if x_with_images_summary: custom_headers["X-With-Images-Summary"] = x_with_images_summary
        if x_retain_images: custom_headers["X-Retain-Images"] = x_retain_images
        if x_no_cache is not None: custom_headers["X-No-Cache"] = str(x_no_cache).lower()
        if x_with_generated_alt is not None: custom_headers["X-With-Generated-Alt"] = str(x_with_generated_alt).lower()
        if x_respond_with: custom_headers["X-Respond-With"] = x_respond_with
        if x_with_favicon is not None: custom_headers["X-With-Favicon"] = str(x_with_favicon).lower()
        if x_return_format: custom_headers["X-Return-Format"] = x_return_format
        if x_engine: custom_headers["X-Engine"] = x_engine
        if x_with_favicons is not None: custom_headers["X-With-Favicons"] = str(x_with_favicons).lower()
        if x_timeout is not None: custom_headers["X-Timeout"] = str(x_timeout)
        if x_set_cookie: custom_headers["X-Set-Cookie"] = x_set_cookie
        if x_proxy_url: custom_headers["X-Proxy-Url"] = x_proxy_url
        if x_locale: custom_headers["X-Locale"] = x_locale

        return self._make_request("POST", api_url, json_data=payload, custom_headers=custom_headers)

    # 5. DeepSearch API
    def call_deepsearch(self, model: str, messages: list, stream: bool = None,
                        reasoning_effort: str = None, budget_tokens: int = None,
                        max_attempts: int = None, no_direct_answer: bool = None,
                        max_returned_urls: int = None, response_format: dict = None,
                        boost_hostnames: list = None, bad_hostnames: list = None,
                        only_hostnames: list = None):
        url = "https://deepsearch.jina.ai/v1/chat/completions"
        payload = {
            "model": model,
            "messages": messages
        }
        if stream is not None: payload["stream"] = stream
        if reasoning_effort: payload["reasoning_effort"] = reasoning_effort
        if budget_tokens is not None: payload["budget_tokens"] = budget_tokens
        if max_attempts is not None: payload["max_attempts"] = max_attempts
        if no_direct_answer is not None: payload["no_direct_answer"] = no_direct_answer
        if max_returned_urls is not None: payload["max_returned_urls"] = max_returned_urls
        if response_format: payload["response_format"] = response_format
        if boost_hostnames: payload["boost_hostnames"] = boost_hostnames
        if bad_hostnames: payload["bad_hostnames"] = bad_hostnames
        if only_hostnames: payload["only_hostnames"] = only_hostnames
        return self._make_request("POST", url, json_data=payload)

    # 6. Segmenter API
    def call_segmenter(self, content: str, tokenizer: str = None, return_tokens: bool = None,
                       return_chunks: bool = None, max_chunk_length: int = None,
                       head: int = None, tail: int = None):
        url = "https://segment.jina.ai/"
        payload = {"content": content}
        if tokenizer: payload["tokenizer"] = tokenizer
        if return_tokens is not None: payload["return_tokens"] = return_tokens
        if return_chunks is not None: payload["return_chunks"] = return_chunks
        if max_chunk_length is not None: payload["max_chunk_length"] = max_chunk_length
        if head is not None: payload["head"] = head
        if tail is not None: payload["tail"] = tail
        return self._make_request("POST", url, json_data=payload)

    # 7. Classifier API (Unified internal method)
    def call_classifier(self, input_data: list, labels: list, model: str = None, classifier_id: str = None):
        url = "https://api.jina.ai/v1/classify"
        payload = {
            "input": input_data,
            "labels": labels
        }
        if model: payload["model"] = model
        if classifier_id: payload["classifier_id"] = classifier_id
        return self._make_request("POST", url, json_data=payload)

def get_jina_ai_tools(jina_client: JinaAIAPIClient):
    """
    Returns a list of MCP tool definitions for Jina AI APIs.
    """
    tools = []

    # 1. Embeddings API Tool
    tools.append({
        "name": "jina_embeddings",
        "description": "Convert text/images to fixed-length vectors for semantic search, similarity matching, clustering, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "Identifier of the model to use.",
                    "enum": ["jina-clip-v2", "jina-embeddings-v3"]
                },
                "input_data": {
                    "type": "array",
                    "description": "Array of input strings or objects to be embedded.",
                    "items": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "object", "properties": {"image": {"type": "string"}}, "required": ["image"]}
                        ]
                    }
                },
                "embedding_type": {
                    "type": "string",
                    "description": "The format of the returned embeddings.",
                    "enum": ["float", "base64", "binary", "ubinary"]
                },
                "task": {
                    "type": "string",
                    "description": "Specifies the intended downstream application to optimize embedding output.",
                    "enum": ["retrieval.query", "retrieval.passage", "text-matching", "classification", "separation"]
                },
                "dimensions": {
                    "type": "integer",
                    "description": "Truncates output embeddings to the specified size if set."
                },
                "normalized": {
                    "type": "boolean",
                    "description": "If true, embeddings are normalized to unit L2 norm."
                },
                "late_chunking": {
                    "type": "boolean",
                    "description": "If true, concatenates all sentences in input and treats as a single input for late chunking."
                },
                "truncate": {
                    "type": "boolean",
                    "description": "If true, the model will automatically drop the tail that extends beyond the maximum context length allowed by the model instead of throwing an error."
                }
            },
            "required": ["model", "input_data"],
            "additionalProperties": False
        },
        "execute": lambda **kwargs: jina_client.call_embeddings(
            model=kwargs["model"],
            input_data=kwargs["input_data"],
            embedding_type=kwargs.get("embedding_type"),
            task=kwargs.get("task"),
            dimensions=kwargs.get("dimensions"),
            normalized=kwargs.get("normalized"),
            late_chunking=kwargs.get("late_chunking"),
            truncate=kwargs.get("truncate")
        )
    })

    # 2. Reranker API Tool
    tools.append({
        "name": "jina_rerank",
        "description": "Find the most relevant search results by refining search results or RAG contextual chunks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "Identifier of the model to use.",
                    "enum": ["jina-reranker-m0", "jina-reranker-v2-base-multilingual", "jina-colbert-v2"]
                },
                "query": {
                    "type": "string",
                    "description": "The search query."
                },
                "documents": {
                    "type": "array",
                    "description": "A list of strings and/or images to rerank.",
                    "items": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
                            {"type": "object", "properties": {"image": {"type": "string"}}, "required": ["image"]}
                        ]
                    }
                },
                "top_n": {
                    "type": "integer",
                    "description": "The number of most relevant documents or indices to return, defaults to the length of documents."
                },
                "return_documents": {
                    "type": "boolean",
                    "description": "If false, returns only the index and relevance score without the document text. If true, returns the index, text, and relevance score."
                }
            },
            "required": ["model", "query", "documents"],
            "additionalProperties": False
        },
        "execute": lambda **kwargs: jina_client.call_reranker(
            model=kwargs["model"],
            query=kwargs["query"],
            documents=kwargs["documents"],
            top_n=kwargs.get("top_n"),
            return_documents=kwargs.get("return_documents")
        )
    })

    # 3. Reader API Tool
    tools.append({
        "name": "jina_reader",
        "description": "Retrieve and parse content from a URL in a format optimized for downstream tasks like LLMs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to retrieve content from."
                },
                "viewport": {
                    "type": "object",
                    "description": "Sets browser viewport dimensions for responsive rendering.",
                    "properties": {
                        "width": {"type": "integer"},
                        "height": {"type": "integer"}
                    },
                    "required": ["width", "height"]
                },
                "inject_page_script": {
                    "type": "string",
                    "description": "Executes preprocessing JS code (inline string or remote URL), for instance manipulating DOMs."
                },
                "x_engine": {
                    "type": "string",
                    "description": "Specifies the engine to retrieve/parse content.",
                    "enum": ["browser", "direct", "cf-browser-rendering"]
                },
                "x_timeout": {
                    "type": "integer",
                    "description": "Specifies the maximum time (in seconds) to wait for the webpage to load."
                },
                "x_target_selector": {
                    "type": "string",
                    "description": "CSS selectors to focus on specific elements within the page."
                },
                "x_wait_for_selector": {
                    "type": "string",
                    "description": "CSS selectors to wait for specific elements before returning."
                },
                "x_remove_selector": {
                    "type": "string",
                    "description": "CSS selectors to exclude certain parts of the page (e.g., headers, footers)."
                },
                "x_with_links_summary": {
                    "type": "string",
                    "description": "Gather all links ('all') or unique links ('true') at the end of the response.",
                    "enum": ["all", "true"]
                },
                "x_with_images_summary": {
                    "type": "string",
                    "description": "Gather all images ('all') or unique images ('true') at the end of the response.",
                    "enum": ["all", "true"]
                },
                "x_with_generated_alt": {
                    "type": "boolean",
                    "description": "Add alt text to images lacking captions."
                },
                "x_no_cache": {
                    "type": "boolean",
                    "description": "Bypass cache for fresh retrieval."
                },
                "x_with_iframe": {
                    "type": "boolean",
                    "description": "Include iframe content in the response."
                },
                "x_return_format": {
                    "type": "string",
                    "description": "Desired return format.",
                    "enum": ["markdown", "html", "text", "screenshot", "pageshot"]
                },
                "x_token_budget": {
                    "type": "integer",
                    "description": "Specifies maximum number of tokens to use for the request."
                },
                "x_retain_images": {
                    "type": "string",
                    "description": "Use 'none' to remove all images from the response.",
                    "enum": ["none"]
                },
                "x_respond_with": {
                    "type": "string",
                    "description": "Use 'readerlm-v2' for high-quality HTML-to-Markdown results."
                },
                "x_set_cookie": {
                    "type": "string",
                    "description": "Forwards custom cookie settings (e.g., 'name=value')."
                },
                "x_proxy_url": {
                    "type": "string",
                    "description": "Utilizes your proxy to access URLs."
                },
                "x_proxy": {
                    "type": "string",
                    "description": "Sets country code for location-based proxy server ('auto' or 'none')."
                },
                "dnt": {
                    "type": "integer",
                    "description": "Use 1 to not cache and track the requested URL on our server."
                },
                "x_no_gfm": {
                    "type": "boolean",
                    "description": "Opt in/out features from GFM (Github Flavored Markdown). Use 'true' to disable, 'table' to opt out GFM Table."
                },
                "x_locale": {
                    "type": "string",
                    "description": "Controls the browser locale to render the page."
                },
                "x_robots_txt": {
                    "type": "string",
                    "description": "Defines bot User-Agent to check against robots.txt."
                },
                "x_with_shadow_dom": {
                    "type": "boolean",
                    "description": "Extract content from all Shadow DOM roots."
                },
                "x_base": {
                    "type": "string",
                    "description": "Use 'final' to follow the full redirect chain."
                },
                "x_md_heading_style": {
                    "type": "string",
                    "description": "When to use '#' or '===' to create Markdown headings. Set 'atx' to use '==' or '--'."
                },
                "x_md_hr": {
                    "type": "string",
                    "description": "Defines Markdown horizontal rule format (passed to Turndown). Default is '***'."
                },
                "x_md_bullet_list_marker": {
                    "type": "string",
                    "description": "Sets Markdown bullet list marker character (passed to Turndown). Options: *, -, +.",
                    "enum": ["*", "-", "+"]
                },
                "x_md_em_delimiter": {
                    "type": "string",
                    "description": "Defines Markdown emphasis delimiter (passed to Turndown). Options: -, *.",
                    "enum": ["-", "*"]
                },
                "x_md_strong_delimiter": {
                    "type": "string",
                    "description": "Sets Markdown strong emphasis delimiter (passed to Turndown). Options: **, __.",
                    "enum": ["**", "__"]
                },
                "x_md_link_style": {
                    "type": "string",
                    "description": "When not set, links are embedded directly. 'referenced' to list links at the end, 'discarded' to replace links with anchor text.",
                    "enum": ["referenced", "discarded"]
                },
                "x_md_link_reference_style": {
                    "type": "string",
                    "description": "Sets Markdown reference link format ('collapse', 'shortcut').",
                    "enum": ["collapse", "shortcut"]
                }
            },
            "required": ["url"],
            "additionalProperties": False
        },
        "execute": lambda **kwargs: jina_client.call_reader(
            url=kwargs["url"],
            viewport=kwargs.get("viewport"),
            inject_page_script=kwargs.get("inject_page_script"),
            x_engine=kwargs.get("x_engine"),
            x_timeout=kwargs.get("x_timeout"),
            x_target_selector=kwargs.get("x_target_selector"),
            x_wait_for_selector=kwargs.get("x_wait_for_selector"),
            x_remove_selector=kwargs.get("x_remove_selector"),
            x_with_links_summary=kwargs.get("x_with_links_summary"),
            x_with_images_summary=kwargs.get("x_with_images_summary"),
            x_with_generated_alt=kwargs.get("x_with_generated_alt"),
            x_no_cache=kwargs.get("x_no_cache"),
            x_with_iframe=kwargs.get("x_with_iframe"),
            x_return_format=kwargs.get("x_return_format"),
            x_token_budget=kwargs.get("x_token_budget"),
            x_retain_images=kwargs.get("x_retain_images"),
            x_respond_with=kwargs.get("x_respond_with"),
            x_set_cookie=kwargs.get("x_set_cookie"),
            x_proxy_url=kwargs.get("x_proxy_url"),
            x_proxy=kwargs.get("x_proxy"),
            dnt=kwargs.get("dnt"),
            x_no_gfm=kwargs.get("x_no_gfm"),
            x_locale=kwargs.get("x_locale"),
            x_robots_txt=kwargs.get("x_robots_txt"),
            x_with_shadow_dom=kwargs.get("x_with_shadow_dom"),
            x_base=kwargs.get("x_base"),
            x_md_heading_style=kwargs.get("x_md_heading_style"),
            x_md_hr=kwargs.get("x_md_hr"),
            x_md_bullet_list_marker=kwargs.get("x_md_bullet_list_marker"),
            x_md_em_delimiter=kwargs.get("x_md_em_delimiter"),
            x_md_strong_delimiter=kwargs.get("x_md_strong_delimiter"),
            x_md_link_style=kwargs.get("x_md_link_style"),
            x_md_link_reference_style=kwargs.get("x_md_link_reference_style")
        )
    })

    # 4. Search API Tool
    tools.append({
        "name": "jina_search",
        "description": "Search the web for information and return results optimized for LLMs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Search query."
                },
                "gl": {
                    "type": "string",
                    "description": "The country to use for the search (two-letter code)."
                },
                "location": {
                    "type": "string",
                    "description": "From where you want the search query to originate (city level recommended)."
                },
                "hl": {
                    "type": "string",
                    "description": "The language to use for the search (two-letter code)."
                },
                "num": {
                    "type": "integer",
                    "description": "Sets maximum results returned."
                },
                "page": {
                    "type": "integer",
                    "description": "The result offset for pagination."
                },
                "x_site": {
                    "type": "string",
                    "description": "For in-site searches limited to the given domain."
                },
                "x_with_links_summary": {
                    "type": "string",
                    "description": "Gather all links ('all') or unique links ('true') at the end of the response.",
                    "enum": ["all", "true"]
                },
                "x_with_images_summary": {
                    "type": "string",
                    "description": "Gather all images ('all') or unique images ('true') at the end of the response.",
                    "enum": ["all", "true"]
                },
                "x_retain_images": {
                    "type": "string",
                    "description": "Use 'none' to remove all images from the response.",
                    "enum": ["none"]
                },
                "x_no_cache": {
                    "type": "boolean",
                    "description": "Bypass cache and retrieve real-time data."
                },
                "x_with_generated_alt": {
                    "type": "boolean",
                    "description": "Generate captions for images without alt tags."
                },
                "x_respond_with": {
                    "type": "string",
                    "description": "Use 'no-content' to exclude page content from the response."
                },
                "x_with_favicon": {
                    "type": "boolean",
                    "description": "Include favicon of the website in the response."
                },
                "x_return_format": {
                    "type": "string",
                    "description": "Desired return format.",
                    "enum": ["markdown", "html", "text", "screenshot", "pageshot"]
                },
                "x_engine": {
                    "type": "string",
                    "description": "Specifies the engine to retrieve/parse content.",
                    "enum": ["browser", "direct"]
                },
                "x_with_favicons": {
                    "type": "boolean",
                    "description": "Fetch the favicon of each URL in the SERP and include them."
                },
                "x_timeout": {
                    "type": "integer",
                    "description": "Specifies the maximum time (in seconds) to wait for the webpage to load."
                },
                "x_set_cookie": {
                    "type": "string",
                    "description": "Forwards custom cookie settings."
                },
                "x_proxy_url": {
                    "type": "string",
                    "description": "Utilizes your proxy to access URLs."
                },
                "x_locale": {
                    "type": "string",
                    "description": "Controls the browser locale to render the page."
                }
            },
            "required": ["q"],
            "additionalProperties": False
        },
        "execute": lambda **kwargs: jina_client.call_search(
            q=kwargs["q"],
            gl=kwargs.get("gl"),
            location=kwargs.get("location"),
            hl=kwargs.get("hl"),
            num=kwargs.get("num"),
            page=kwargs.get("page"),
            x_site=kwargs.get("x_site"),
            x_with_links_summary=kwargs.get("x_with_links_summary"),
            x_with_images_summary=kwargs.get("x_with_images_summary"),
            x_retain_images=kwargs.get("x_retain_images"),
            x_no_cache=kwargs.get("x_no_cache"),
            x_with_generated_alt=kwargs.get("x_with_generated_alt"),
            x_respond_with=kwargs.get("x_respond_with"),
            x_with_favicon=kwargs.get("x_with_favicon"),
            x_return_format=kwargs.get("x_return_format"),
            x_engine=kwargs.get("x_engine"),
            x_with_favicons=kwargs.get("x_with_favicons"),
            x_timeout=kwargs.get("x_timeout"),
            x_set_cookie=kwargs.get("x_set_cookie"),
            x_proxy_url=kwargs.get("x_proxy_url"),
            x_locale=kwargs.get("x_locale")
        )
    })

    # 5. DeepSearch API Tool
    tools.append({
        "name": "jina_deepsearch",
        "description": "Combines web searching, reading, and reasoning for comprehensive investigation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "ID of the model to use."
                },
                "messages": {
                    "type": "array",
                    "description": "A list of messages between the user and the assistant comprising the conversation so far.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["role", "content"]
                    }
                },
                "stream": {
                    "type": "boolean",
                    "description": "Delivers events as they occur through server-sent events."
                },
                "reasoning_effort": {
                    "type": "string",
                    "description": "Constrains effort on reasoning for reasoning models.",
                    "enum": ["low", "medium", "high"]
                },
                "budget_tokens": {
                    "type": "integer",
                    "description": "Maximum number of tokens allowed for DeepSearch process."
                },
                "max_attempts": {
                    "type": "integer",
                    "description": "Maximum number of retries for solving a problem in DeepSearch process."
                },
                "no_direct_answer": {
                    "type": "boolean",
                    "description": "Forces the model to take further thinking/search steps even when the query seems trivial."
                },
                "max_returned_urls": {
                    "type": "integer",
                    "description": "The maximum number of URLs to include in the final answer/chunk."
                },
                "response_format": {
                    "type": "object",
                    "description": "Enables Structured Outputs, ensuring final answer matches supplied JSON schema.",
                    "properties": {
                        "type": {"type": "string", "enum": ["json_schema"]},
                        "json_schema": {"type": "object"}
                    },
                    "required": ["type", "json_schema"]
                },
                "boost_hostnames": {
                    "type": "array",
                    "description": "A list of domains that are given a higher priority for content retrieval.",
                    "items": {"type": "string"}
                },
                "bad_hostnames": {
                    "type": "array",
                    "description": "A list of domains to be strictly excluded from content retrieval.",
                    "items": {"type": "string"}
                },
                "only_hostnames": {
                    "type": "array",
                    "description": "A list of domains to be exclusively included in content retrieval.",
                    "items": {"type": "string"}
                }
            },
            "required": ["model", "messages"],
            "additionalProperties": False
        },
        "execute": lambda **kwargs: jina_client.call_deepsearch(
            model=kwargs["model"],
            messages=kwargs["messages"],
            stream=kwargs.get("stream"),
            reasoning_effort=kwargs.get("reasoning_effort"),
            budget_tokens=kwargs.get("budget_tokens"),
            max_attempts=kwargs.get("max_attempts"),
            no_direct_answer=kwargs.get("no_direct_answer"),
            max_returned_urls=kwargs.get("max_returned_urls"),
            response_format=kwargs.get("response_format"),
            boost_hostnames=kwargs.get("boost_hostnames"),
            bad_hostnames=kwargs.get("bad_hostnames"),
            only_hostnames=kwargs.get("only_hostnames")
        )
    })

    # 6. Segmenter API Tool
    tools.append({
        "name": "jina_segmenter",
        "description": "Tokenizes text and divides text into chunks for downstream applications like RAG.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The text content to segment."
                },
                "tokenizer": {
                    "type": "string",
                    "description": "Specifies the tokenizer to use.",
                    "enum": ["cl100k_base", "o200k_base", "p50k_base", "r50k_base", "p50k_edit", "gpt2"]
                },
                "return_tokens": {
                    "type": "boolean",
                    "description": "If true, includes tokens and their IDs in the response."
                },
                "return_chunks": {
                    "type": "boolean",
                    "description": "If true, segments the text into semantic chunks."
                },
                "max_chunk_length": {
                    "type": "integer",
                    "description": "Maximum characters per chunk (only effective if 'return_chunks' is true)."
                },
                "head": {
                    "type": "integer",
                    "description": "Returns the first N tokens (exclusive with 'tail')."
                },
                "tail": {
                    "type": "integer",
                    "description": "Returns the last N tokens (exclusive with 'head')."
                }
            },
            "required": ["content"],
            "additionalProperties": False
        },
        "execute": lambda **kwargs: jina_client.call_segmenter(
            content=kwargs["content"],
            tokenizer=kwargs.get("tokenizer"),
            return_tokens=kwargs.get("return_tokens"),
            return_chunks=kwargs.get("return_chunks"),
            max_chunk_length=kwargs.get("max_chunk_length"),
            head=kwargs.get("head"),
            tail=kwargs.get("tail")
        )
    })

    # 7. Classifier API Tool (Text)
    tools.append({
        "name": "jina_classify_text",
        "description": "Perform zero-shot classification for text content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "input_data": {
                    "type": "array",
                    "description": "Array of text inputs for classification.",
                    "items": {"type": "string"}
                },
                "labels": {
                    "type": "array",
                    "description": "List of labels used for classification.",
                    "items": {"type": "string"}
                },
                "model": {
                    "type": "string",
                    "description": "Identifier of the model to use. Defaults to 'jina-embeddings-v3'.",
                    "default": "jina-embeddings-v3",
                    "enum": ["jina-embeddings-v3"]
                },
                "classifier_id": {
                    "type": "string",
                    "description": "The identifier of the classifier. If not provided, a new classifier will be created."
                }
            },
            "required": ["input_data", "labels"],
            "additionalProperties": False
        },
        "execute": lambda **kwargs: jina_client.call_classifier(
            input_data=kwargs["input_data"],
            labels=kwargs["labels"],
            model=kwargs.get("model", "jina-embeddings-v3"), # Apply default at execution
            classifier_id=kwargs.get("classifier_id")
        )
    })

    # 8. Classifier API Tool (Image)
    tools.append({
        "name": "jina_classify_image",
        "description": "Perform zero-shot classification for image content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "input_data": {
                    "type": "array",
                    "description": "Array of image inputs for classification. Each entry should be an object with an 'image' key (base64-encoded string).",
                    "items": {
                        "type": "object",
                        "properties": {"image": {"type": "string"}},
                        "required": ["image"]
                    }
                },
                "labels": {
                    "type": "array",
                    "description": "List of labels used for classification.",
                    "items": {"type": "string"}
                },
                "model": {
                    "type": "string",
                    "description": "Identifier of the model to use. Defaults to 'jina-clip-v2'.",
                    "default": "jina-clip-v2",
                    "enum": ["jina-clip-v2"]
                },
                "classifier_id": {
                    "type": "string",
                    "description": "The identifier of the classifier. If not provided, a new classifier will be created."
                }
            },
            "required": ["input_data", "labels"],
            "additionalProperties": False
        },
        "execute": lambda **kwargs: jina_client.call_classifier(
            input_data=kwargs["input_data"],
            labels=kwargs["labels"],
            model=kwargs.get("model", "jina-clip-v2"), # Apply default at execution
            classifier_id=kwargs.get("classifier_id")
        )
    })

    return tools