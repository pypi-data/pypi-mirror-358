from __future__ import annotations

from collections import deque
from typing import List
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def crawl_urls(start_url: str, max_pages: int = 10) -> List[str]:
    """Crawl a website starting at ``start_url`` and collect up to ``max_pages`` unique URLs.

    Only URLs that share the same domain and start with the same path prefix as
    ``start_url`` are included.
    """
    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc
    base_path = parsed_start.path
    if not base_path.endswith('/'):
        base_path = parsed_start.path.rstrip('/') + '/'

    visited: set[str] = set()
    queued: set[str] = set()  # Added this line to define `queued`
    queue: deque[str] = deque([start_url])
    collected: List[str] = []

    while queue and len(collected) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        try:
            resp = requests.get(url, timeout=10)
            html = resp.text
        except requests.RequestException:
            continue

        collected.append(url)
        if len(collected) >= max_pages:
            break

        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a['href'])
            parsed = urlparse(link)
            if parsed.netloc != base_domain:
                continue
            if not parsed.path.startswith(base_path):
                continue
            normalized = parsed._replace(fragment="").geturl()
            if normalized not in visited and normalized not in queued:
                queue.append(normalized)
                queued.add(normalized)
    return collected
