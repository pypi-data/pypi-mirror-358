"""MCP Llms-txt server for docs."""

import os
from urllib.parse import urlparse
import urllib.parse

import httpx
from markdownify import markdownify
from mcp.server.fastmcp import FastMCP
from typing_extensions import NotRequired, TypedDict

from .link_extractor import LinkExtractor


class DocSource(TypedDict):
    """A source of documentation for a library or a package."""

    name: NotRequired[str]
    """Name of the documentation source (optional)."""

    llms_txt: str
    """URL to the llms.txt file or documentation source."""

    description: NotRequired[str]
    """Description of the documentation source (optional)."""


def extract_domain(url: str) -> str:
    """Extract domain from URL.

    Args:
        url: Full URL

    Returns:
        Domain with scheme and trailing slash (e.g., https://example.com/)
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/"


def _is_http_or_https(url: str) -> bool:
    """Check if the URL is an HTTP or HTTPS URL."""
    return url.startswith(("http:", "https:"))


def _get_fetch_description(has_local_sources: bool) -> str:
    """Get fetch docs tool description."""
    description = [
        "Fetch and parse documentation from a given URL or local file.",
        "",
        "Use this tool after list_doc_sources to:",
        "1. First fetch the llms.txt file from a documentation source",
        "2. Analyze the URLs listed in the llms.txt file",
        "3. Then fetch specific documentation pages relevant to the user's question",
        "",
    ]

    if has_local_sources:
        description.extend(
            [
                "Args:",
                "    url: The URL or file path to fetch documentation from. Can be:",
                "        - URL from an allowed domain",
                "        - A local file path (absolute or relative)",
                "        - A file:// URL (e.g., file:///path/to/llms.txt)",
            ]
        )
    else:
        description.extend(
            [
                "Args:",
                "    url: The URL to fetch documentation from.",
            ]
        )

    description.extend(
        [
            "",
            "Returns:",
            "    The fetched documentation content converted to markdown, or an error message",  # noqa: E501
            "    if the request fails or the URL is not from an allowed domain.",
        ]
    )

    return "\n".join(description)


def _normalize_path(path: str) -> str:
    """Accept paths in file:/// or relative format and map to absolute paths."""
    return (
        os.path.abspath(path[7:])
        if path.startswith("file://")
        else os.path.abspath(path)
    )


def _is_searchable_source(url: str) -> bool:
    """Check if the source supports search functionality."""
    return "docparser.agentium.ru" in url


def _build_search_url(source_url: str, query: str) -> str:
    """Build search URL from source URL and query."""
    # Transform .../index → .../search?q=query&limit=10
    if source_url.endswith("/index"):
        base_url = source_url.replace("/index", "/search")
    else:
        base_url = source_url.rstrip("/") + "/search"
    
    encoded_query = urllib.parse.quote_plus(query)
    return f"{base_url}?q={encoded_query}&limit=10"


def _format_search_results(data: dict) -> str:
    """Format search results for AI assistant."""
    query = data.get("query", "")
    project = data.get("project", "")
    results = data.get("results", [])[:10]  # Top 10
    
    output = [
        f"# 🔍 Результаты поиска в {project}",
        f"",
        f"**Запрос:** '{query}'",
        f"**Найдено:** {len(results)} результатов",
        f""
    ]
    
    for i, result in enumerate(results, 1):
        title = result.get("title", "Без названия")
        snippet = result.get("snippet", "")
        # Truncate snippet if too long
        if len(snippet) > 150:
            snippet = snippet[:150] + "..."
        url = result.get("url", "")
        score = result.get("relevance_score", 0)
        
        output.extend([
            f"## {i}. {title}",
            f"**Релевантность:** {score}",  
            f"**Описание:** {snippet}",
            f"**URL:** https://docparser.agentium.ru{url}",
            f""
        ])
    
    output.extend([
        f"---",
        f"💡 Используйте `fetch_docs()` для получения полного содержимого"
    ])
    
    return "\n".join(output)


def create_server(
    doc_sources: list[DocSource],
    *,
    follow_redirects: bool = False,
    timeout: float = 10,
    settings: dict | None = None,
    allowed_domains: list[str] | None = None,
) -> FastMCP:
    """Create the server and generate documentation retrieval tools.

    Args:
        doc_sources: List of documentation sources to make available
        follow_redirects: Whether to follow HTTP redirects when fetching docs
        timeout: HTTP request timeout in seconds
        settings: Additional settings to pass to FastMCP
        allowed_domains: Additional domains to allow fetching from.
            Use ['*'] to allow all domains
            The domain hosting the llms.txt file is always appended to the list
            of allowed domains.

    Returns:
        A FastMCP server instance configured with documentation tools
    """
    settings = settings or {}
    server = FastMCP(
        name="llms-txt",
        instructions=(
            "Use the list doc sources tool to see available documentation "
            "sources. Use search_docs to find specific information with intelligent "
            "search on supported sources. Use browse_page to navigate hierarchical "
            "documentation and see available links. Use fetch_docs to get specific "
            "documents."
        ),
        **settings,
    )
    httpx_client = httpx.AsyncClient(follow_redirects=follow_redirects, timeout=timeout)

    local_sources = []
    remote_sources = []

    for entry in doc_sources:
        url = entry["llms_txt"]
        if _is_http_or_https(url):
            remote_sources.append(entry)
        else:
            local_sources.append(entry)

    # Let's verify that all local sources exist
    for entry in local_sources:
        path = entry["llms_txt"]
        abs_path = _normalize_path(path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Local file not found: {abs_path}")

    # Parse the domain names in the llms.txt URLs and identify local file paths
    domains = set(extract_domain(entry["llms_txt"]) for entry in remote_sources)

    # Add additional allowed domains if specified, or set to '*' if we have local files
    if allowed_domains:
        if "*" in allowed_domains:
            domains = {"*"}  # Special marker for allowing all domains
        else:
            domains.update(allowed_domains)

    allowed_local_files = set(
        _normalize_path(entry["llms_txt"]) for entry in local_sources
    )

    @server.tool()
    def list_doc_sources() -> str:
        """List all available documentation sources.

        This is the first tool you should call in the documentation workflow.
        It provides URLs to llms.txt files or local file paths that the user has made available.

        Returns:
            A string containing a formatted list of documentation sources with their URLs or file paths
        """
        content = ""
        for entry_ in doc_sources:
            url_or_path = entry_["llms_txt"]

            if _is_http_or_https(url_or_path):
                name = entry_.get("name", extract_domain(url_or_path))
                content += f"{name}\nURL: {url_or_path}\n\n"
            else:
                path = _normalize_path(url_or_path)
                name = entry_.get("name", path)
                content += f"{name}\nPath: {path}\n\n"
        return content

    fetch_docs_description = _get_fetch_description(
        has_local_sources=bool(local_sources)
    )

    @server.tool(description=fetch_docs_description)
    async def fetch_docs(url: str) -> str:
        nonlocal domains
        # Handle local file paths (either as file:// URLs or direct filesystem paths)
        if not _is_http_or_https(url):
            abs_path = _normalize_path(url)
            if abs_path not in allowed_local_files:
                raise ValueError(
                    f"Local file not allowed: {abs_path}. Allowed files: {allowed_local_files}"
                )
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return markdownify(content)
            except Exception as e:
                return f"Error reading local file: {str(e)}"
        else:
            # Otherwise treat as URL
            if "*" not in domains and not any(
                url.startswith(domain) for domain in domains
            ):
                return (
                    "Error: URL not allowed. Must start with one of the following domains: "
                    + ", ".join(domains)
                )

            try:
                response = await httpx_client.get(url, timeout=timeout)
                response.raise_for_status()
                return markdownify(response.text)
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                return f"Encountered an HTTP error: {str(e)}"

    @server.tool()
    async def browse_page(url: str) -> str:
        """Browse a page and extract all links for navigation.
        
        Universal tool for navigating any documentation.
        Shows page content and all available links without assumptions about page type.
        
        Args:
            url: URL of the page to browse
            
        Returns:
            Page content + list of all found links
        """
        nonlocal domains
        
        # Use the same security logic as fetch_docs
        if not _is_http_or_https(url):
            abs_path = _normalize_path(url)
            if abs_path not in allowed_local_files:
                return f"Local file not allowed: {abs_path}"
            
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                return f"Error reading file: {str(e)}"
        else:
            # Check domain permission
            if "*" not in domains and not any(
                url.startswith(domain) for domain in domains
            ):
                return f"Domain not allowed: {urlparse(url).netloc}"
            
            try:
                response = await httpx_client.get(url, timeout=timeout)
                response.raise_for_status()
                content = response.text
            except Exception as e:
                return f"Error fetching page: {str(e)}"
        
        # Convert to markdown
        markdown_content = markdownify(content)
        
        # Extract links
        extractor = LinkExtractor()
        links = extractor.extract_all_links(content, url)
        
        # Format response
        result = f"# Содержимое страницы\n\n{markdown_content}\n\n"
        
        if links:
            result += "# Найденные ссылки\n\n"
            for i, link in enumerate(links, 1):
                result += f"{i}. **{link.title}**\n   URL: {link.url}\n\n"
        else:
            result += "# Ссылки не найдены\n\nЭто конечный документ или страница без ссылок.\n"
        
        return result

    @server.tool()
    async def search_docs(source_url: str, query: str) -> str:
        """Search documentation with intelligent fallback to browsing.
        
        Performs semantic search on supported sources (DocParser API) with automatic
        fallback to page browsing when search is not available.
        
        Args:
            source_url: URL of the documentation source (from list_doc_sources)
            query: Search query to find relevant documentation
            
        Returns:
            Search results with relevance scores or browsed page content as fallback
        """
        nonlocal domains
        
        # Simple search logic
        if _is_searchable_source(source_url):
            search_url = _build_search_url(source_url, query)
            
            # Check domain permission for search URL  
            if "*" not in domains and not any(
                search_url.startswith(domain) for domain in domains
            ):
                return f"Search URL domain not allowed: {urlparse(search_url).netloc}"
            
            try:
                response = await httpx_client.get(search_url, timeout=timeout)
                response.raise_for_status()
                search_data = response.json()
                return _format_search_results(search_data)
            except Exception as e:
                # Search failed, fallback to browse
                fallback_msg = f"🔍 Поиск недоступен ({str(e)}), используем навигацию:\n\n"
                browse_result = await browse_page(source_url)
                return fallback_msg + browse_result
        else:
            # No search support, use browse directly
            fallback_msg = f"🔍 Поиск не поддерживается для этого источника, используем навигацию:\n\n"
            browse_result = await browse_page(source_url)
            return fallback_msg + browse_result

    return server
