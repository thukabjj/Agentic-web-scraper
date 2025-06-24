#!/usr/bin/env python3
"""
Web content fetching adapter using httpx for HTTP requests.
Simplified implementation without browser automation.
"""

import asyncio
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx

from core.domain.models import ContentType, PageContent
from core.domain.ports import WebAdapterPort


class FetchAdapter(WebAdapterPort):
    """HTTP-based web content fetching adapter"""

    def __init__(self):
        self.client_config = {
            "timeout": 30.0,
            "follow_redirects": True,
            "headers": {
                "User-Agent": "Agentic-Web-Scraper/1.0 (Educational Purpose)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        }

    async def fetch_content(self, url: str, content_type: ContentType) -> Optional[PageContent]:
        """
        Fetch content from a URL using HTTP requests

        Args:
            url: Target URL to fetch
            content_type: Expected content type (HTML, JSON, TEXT)

        Returns:
            PageContent object or None if fetch fails
        """
        try:
            async with httpx.AsyncClient(**self.client_config) as client:
                response = await client.get(url)
                response.raise_for_status()

                # Get content based on type
                if content_type == ContentType.JSON:
                    try:
                        content = response.json()
                        text_content = str(content)
                    except Exception:
                        text_content = response.text
                else:
                    text_content = response.text

                # Extract title from HTML if possible
                title = None
                if content_type == ContentType.HTML and text_content:
                    try:
                        import re
                        title_match = re.search(r'<title[^>]*>(.*?)</title>',
                                              text_content, re.IGNORECASE | re.DOTALL)
                        if title_match:
                            title = title_match.group(1).strip()
                    except Exception:
                        pass

                return PageContent(
                    url=url,
                    content=text_content,
                    timestamp=datetime.now(),
                    content_type=content_type,
                    title=title,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )

        except httpx.HTTPStatusError as e:
            print(f"HTTP error {e.response.status_code} for {url}")
            return None
        except httpx.RequestError as e:
            print(f"Request error for {url}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching {url}: {e}")
            return None

    async def fetch_multiple(self, urls: list[str], content_type: ContentType) -> list[Optional[PageContent]]:
        """
        Fetch content from multiple URLs concurrently

        Args:
            urls: List of URLs to fetch
            content_type: Expected content type

        Returns:
            List of PageContent objects (None for failed fetches)
        """
        tasks = [self.fetch_content(url, content_type) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and accessible"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and parsed.scheme in ('http', 'https')
        except Exception:
            return False

    async def get_page_links(self, url: str) -> list[str]:
        """Extract links from a webpage"""
        content = await self.fetch_content(url, ContentType.HTML)
        if not content:
            return []

        links = []
        try:
            import re

            # Simple regex to extract href attributes
            href_pattern = r'href=[\'"](.*?)[\'"]'
            matches = re.findall(href_pattern, content.content, re.IGNORECASE)

            for match in matches:
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, match)
                if self.is_valid_url(absolute_url):
                    links.append(absolute_url)
        except Exception:
            pass

        return list(set(links))  # Remove duplicates
