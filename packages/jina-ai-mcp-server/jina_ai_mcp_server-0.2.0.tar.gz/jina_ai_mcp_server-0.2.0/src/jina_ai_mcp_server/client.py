import requests
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
        url = "https://api.jina.ai/v1/rerank"  # Fixed URL
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