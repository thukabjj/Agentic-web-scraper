#!/usr/bin/env python3
"""
Playwright-based web content fetching adapter for JavaScript-heavy sites.
Handles dynamic content loading, cookie consent, and modern web applications.
"""

import asyncio
from datetime import datetime
from typing import Optional

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from core.domain.models import ContentType, PageContent
from core.domain.ports import WebAdapterPort


class PlaywrightAdapter(WebAdapterPort):
    """Playwright-based web content fetching adapter with JavaScript support"""

    def __init__(self):
        self.browser = None
        self.context = None

    async def start_browser(self):
        """Start browser instance"""
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,  # Run in background
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage'
                ]
            )
            self.context = await self.browser.new_context(
                user_agent=(
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Safari/537.36'
                ),
                viewport={'width': 1920, 'height': 1080}
            )

    async def close_browser(self):
        """Close browser instance"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def fetch_content(
        self,
        url: str,
        content_type: ContentType,
        wait_for_content: bool = True,
        timeout: int = 30
    ) -> Optional[PageContent]:
        """
        Fetch content from a URL using Playwright (handles JavaScript)

        Args:
            url: Target URL to fetch
            content_type: Expected content type (HTML, JSON, TEXT)
            wait_for_content: Whether to wait for dynamic content to load
            timeout: Request timeout in seconds

        Returns:
            PageContent object or None if fetch fails
        """
        await self.start_browser()

        try:
            page = await self.context.new_page()

            # Navigate to the page
            await page.goto(url, timeout=timeout * 1000)

            # Handle common cookie consent patterns
            await self._handle_cookie_consent(page)

            if wait_for_content:
                # Wait for dynamic content to load
                await self._wait_for_financial_data(page, url)

            # Get page content
            content = await page.content()
            title = await page.title()

            # Handle different content types
            if content_type == ContentType.JSON:
                try:
                    # Try to extract JSON from page
                    json_content = await page.evaluate(
                        '() => document.querySelector("pre") ? '
                        'document.querySelector("pre").textContent : null'
                    )
                    if json_content:
                        content = json_content
                except Exception:
                    pass

            await page.close()

            return PageContent(
                url=url,
                content=content,
                timestamp=datetime.now(),
                content_type=content_type,
                title=title,
                status_code=200,
                headers={}
            )

        except PlaywrightTimeoutError:
            print(f"Timeout error for {url}")
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    async def _handle_cookie_consent(self, page):
        """Handle common cookie consent dialogs"""
        consent_selectors = [
            'button:has-text("Accept all")',
            'button:has-text("Accept All")',
            'button:has-text("I agree")',
            'button:has-text("OK")',
            '[data-testid="consent-accept"]',
            '.consent-accept',
            '#consent-accept'
        ]

        for selector in consent_selectors:
            try:
                await page.click(selector, timeout=2000)
                await page.wait_for_timeout(1000)  # Wait for page to update
                break
            except Exception:
                continue

    async def _wait_for_financial_data(self, page, url: str):
        """Wait for financial data to load on common financial and content sites"""
        if 'finance.yahoo.com' in url:
            await self._wait_for_yahoo_finance(page)
        elif 'google.com/finance' in url:
            await self._wait_for_google_finance(page)
        elif 'medium.com' in url:
            await self._wait_for_medium_article(page)
        elif any(site in url for site in ['dev.to', 'hashnode.com', 'substack.com']):
            await self._wait_for_blog_content(page)
        else:
            # Generic wait for content
            await page.wait_for_timeout(3000)

    async def _wait_for_yahoo_finance(self, page):
        """Wait for Yahoo Finance specific content"""
        try:
            # Wait for price container or specific elements
            await page.wait_for_selector(
                '[data-symbol], .Fw\\(b\\).Fz\\(36px\\), .Trsdu\\(0\\.3s\\)',
                timeout=10000
            )
            await page.wait_for_timeout(2000)  # Additional wait for updates
        except Exception:
            await page.wait_for_timeout(5000)  # Fallback wait

    async def _wait_for_google_finance(self, page):
        """Wait for Google Finance specific content"""
        try:
            # Wait for price elements to load
            await page.wait_for_selector(
                '[data-last-price], .YMlKec, .P6K39c',
                timeout=10000
            )
            await page.wait_for_timeout(2000)
        except Exception:
            await page.wait_for_timeout(5000)

    async def _wait_for_medium_article(self, page):
        """Wait for Medium article content to load"""
        try:
            # Wait for article content container
            await page.wait_for_selector(
                'article, [data-testid="storyContent"], .postArticle-content',
                timeout=10000
            )
            await page.wait_for_timeout(3000)  # Additional wait for images/content
        except Exception:
            await page.wait_for_timeout(5000)

    async def _wait_for_blog_content(self, page):
        """Wait for blog content to load"""
        try:
            # Wait for common blog content selectors
            await page.wait_for_selector(
                'article, .post-content, .article-content, main',
                timeout=10000
            )
            await page.wait_for_timeout(2000)
        except Exception:
            await page.wait_for_timeout(5000)

    async def fetch_multiple(
        self,
        urls: list[str],
        content_type: ContentType
    ) -> list[Optional[PageContent]]:
        """Fetch content from multiple URLs"""
        tasks = [self.fetch_content(url, content_type) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        await self.close_browser()  # Clean up after batch
        return results

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return bool(parsed.netloc) and parsed.scheme in ('http', 'https')
        except Exception:
            return False

    async def get_page_links(self, url: str) -> list[str]:
        """Extract links from a webpage"""
        content = await self.fetch_content(url, ContentType.HTML)
        if not content:
            return []

        # Use the existing link extraction from FetchAdapter
        from adapters.web.fetch_adapter import FetchAdapter
        fetch_adapter = FetchAdapter()
        return await fetch_adapter.get_page_links(url)
