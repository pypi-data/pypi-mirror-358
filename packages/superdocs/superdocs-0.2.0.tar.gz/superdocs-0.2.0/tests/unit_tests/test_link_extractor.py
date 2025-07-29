"""Тесты для LinkExtractor."""

import pytest
from superdocs.link_extractor import LinkExtractor, Link


def test_extract_markdown_links():
    """Тест извлечения markdown ссылок."""
    extractor = LinkExtractor()
    content = """
    # Documentation
    
    Check out [Google](https://google.com) and [GitHub](https://github.com).
    Also see [Local File](./local.md) and [Anchor](#section).
    """
    
    links = extractor.extract_all_links(content, "https://example.com/")
    
    # Должно быть 3 ссылки (якорная ссылка исключается)
    assert len(links) == 3
    
    assert links[0].title == "Google"
    assert links[0].url == "https://google.com"
    
    assert links[1].title == "GitHub" 
    assert links[1].url == "https://github.com"
    
    assert links[2].title == "Local File"
    assert links[2].url == "https://example.com/local.md"


def test_extract_html_links():
    """Тест извлечения HTML ссылок."""
    extractor = LinkExtractor()
    content = """
    <html>
    <body>
        <a href="https://example.com">Example</a>
        <a href="/docs/readme.md">Readme</a>
        <a href="#anchor">Skip This</a>
        <a href="javascript:void(0)">Skip JS</a>
    </body>
    </html>
    """
    
    links = extractor.extract_all_links(content, "https://site.com/")
    
    # Должно быть 2 ссылки (якорные и JS исключаются)
    assert len(links) == 2
    
    assert links[0].title == "Example"
    assert links[0].url == "https://example.com"
    
    assert links[1].title == "Readme"
    assert links[1].url == "https://site.com/docs/readme.md"


def test_mixed_content():
    """Тест смешанного Markdown + HTML контента."""
    extractor = LinkExtractor()
    content = """
    # Mixed Content
    
    Markdown link: [MD Link](./markdown.md)
    
    <p>HTML link: <a href="./html.html">HTML Link</a></p>
    """
    
    links = extractor.extract_all_links(content, "https://example.com/docs/")
    
    assert len(links) == 2
    assert links[0].title == "MD Link"
    assert links[0].url == "https://example.com/docs/markdown.md"
    assert links[1].title == "HTML Link"
    assert links[1].url == "https://example.com/docs/html.html"


def test_deduplication():
    """Тест удаления дублирующихся ссылок."""
    extractor = LinkExtractor()
    content = """
    [Google](https://google.com)
    <a href="https://google.com">Google</a>
    [Different Title](https://google.com)
    """
    
    links = extractor.extract_all_links(content, "https://example.com/")
    
    # Должна остаться только одна ссылка на google.com (первая)
    assert len(links) == 1
    assert links[0].title == "Google"
    assert links[0].url == "https://google.com"


def test_empty_content():
    """Тест пустого контента."""
    extractor = LinkExtractor()
    links = extractor.extract_all_links("", "https://example.com/")
    assert len(links) == 0


def test_no_links():
    """Тест контента без ссылок."""
    extractor = LinkExtractor()
    content = """
    # Just Text
    
    This is just plain text without any links.
    Some code: `print("hello")`
    """
    
    links = extractor.extract_all_links(content, "https://example.com/")
    assert len(links) == 0 