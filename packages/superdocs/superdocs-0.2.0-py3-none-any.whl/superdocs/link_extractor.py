"""Простой модуль для извлечения ссылок из документации.

Принцип KISS: извлекает ВСЕ ссылки без попыток классификации или детекции типов.
Универсальность: работает с любым HTML/Markdown контентом.
"""

import re
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from typing import List


@dataclass
class Link:
    """Простое представление ссылки."""
    title: str
    url: str
    description: str = ""


class LinkExtractor:
    """Простой экстрактор ссылок без сложной логики."""
    
    def extract_all_links(self, content: str, base_url: str) -> List[Link]:
        """Извлекает ВСЕ ссылки из контента - markdown и HTML.
        
        Args:
            content: HTML или Markdown контент
            base_url: Базовый URL для построения абсолютных ссылок
            
        Returns:
            Список всех найденных ссылок
        """
        links = []
        
        # Markdown ссылки: [title](url)
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for title, url in markdown_links:
            # Пропускаем якорные ссылки
            if not url.startswith('#'):
                full_url = urljoin(base_url, url)
                links.append(Link(title=title.strip(), url=full_url))
        
        # HTML ссылки: <a href="url">title</a>
        html_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>', content, re.IGNORECASE)
        for url, title in html_links:
            # Пропускаем якорные ссылки и javascript
            if not url.startswith('#') and not url.startswith('javascript:'):
                full_url = urljoin(base_url, url)
                links.append(Link(title=title.strip(), url=full_url))
        
        return self._deduplicate_links(links)
    
    def _deduplicate_links(self, links: List[Link]) -> List[Link]:
        """Удаляет дублирующиеся ссылки по URL."""
        seen = set()
        unique_links = []
        for link in links:
            if link.url not in seen:
                seen.add(link.url)
                unique_links.append(link)
        return unique_links 