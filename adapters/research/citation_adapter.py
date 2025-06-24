#!/usr/bin/env python3
"""
Citation Management Adapter for Deep Research

This adapter provides citation generation, source verification, and
bibliography formatting capabilities.
"""

import re
from datetime import datetime
from typing import Dict, List
from urllib.parse import urlparse

from core.domain.models import Citation, ContentType, PageContent
from core.domain.ports import CitationPort, LLMPort


class CitationAdapter(CitationPort):
    """
    Adapter for managing citations and source tracking
    """

    def __init__(self, llm_adapter: LLMPort):
        self.llm_adapter = llm_adapter

    async def generate_citation(
        self,
        content: PageContent,
        citation_format: str = "apa"
    ) -> Citation:
        """
        Generate a properly formatted citation from page content

        Args:
            content: Page content to cite
            citation_format: Citation format (apa, mla, chicago)

        Returns:
            Citation object with proper formatting
        """
        # Extract metadata from content
        title = content.title or self._extract_title_from_content(content.content)
        author = self._extract_author_from_content(content.content)
        published_date = self._extract_date_from_content(content.content)

        # Create excerpt from content
        excerpt = self._create_excerpt(content.content)

        # Determine source type
        source_type = self._determine_source_type(content.url)

        # Calculate initial reliability score
        reliability_score = await self._calculate_initial_reliability(content)

        citation = Citation(
            url=content.url,
            title=title,
            excerpt=excerpt,
            timestamp=published_date or content.timestamp,
            source_type=source_type,
            reliability_score=reliability_score,
            page_content_id=content.url
        )

        return citation

    async def verify_source_reliability(
        self,
        citation: Citation
    ) -> float:
        """
        Verify the reliability of a source using multiple factors

        Args:
            citation: Citation to verify

        Returns:
            Reliability score between 0.0 and 1.0
        """
        score = 0.5  # Base score

        # Domain authority factor
        domain_score = self._calculate_domain_authority(citation.url)
        score += domain_score * 0.3

        # Source type factor
        type_scores = {
            "academic": 0.9,
            "documentation": 0.8,
            "news": 0.7,
            "government": 0.85,
            "web": 0.4
        }
        score = max(score, type_scores.get(citation.source_type, 0.4))

        # Content quality indicators
        content_score = await self._analyze_content_quality(citation)
        score += content_score * 0.2

        # Recency factor
        if citation.timestamp:
            days_old = (datetime.now() - citation.timestamp).days
            if days_old < 30:
                score += 0.1
            elif days_old < 365:
                score += 0.05

        return min(1.0, max(0.0, score))

    async def format_bibliography(
        self,
        citations: List[Citation],
        format_style: str = "apa"
    ) -> str:
        """
        Format a bibliography from citations

        Args:
            citations: List of citations to format
            format_style: Bibliography style (apa, mla, chicago)

        Returns:
            Formatted bibliography string
        """
        if not citations:
            return ""

        # Remove duplicates based on URL
        unique_citations = {c.url: c for c in citations}.values()

        # Sort by title or author
        sorted_citations = sorted(unique_citations, key=lambda c: c.title.lower())

        bibliography_lines = []

        for citation in sorted_citations:
            if format_style.lower() == "apa":
                formatted = self._format_apa_citation(citation)
            elif format_style.lower() == "mla":
                formatted = self._format_mla_citation(citation)
            elif format_style.lower() == "chicago":
                formatted = self._format_chicago_citation(citation)
            else:
                formatted = self._format_apa_citation(citation)  # Default to APA

            bibliography_lines.append(formatted)

        return "\n\n".join(bibliography_lines)

    def _extract_title_from_content(self, content: str) -> str:
        """Extract title from HTML content"""
        # Try to find title tag
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up title
            title = re.sub(r'<[^>]+>', '', title)  # Remove HTML tags
            return title[:200]  # Limit length

        # Fallback: try to find h1 tag
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        if h1_match:
            title = h1_match.group(1).strip()
            title = re.sub(r'<[^>]+>', '', title)
            return title[:200]

        return "Untitled Document"

    def _extract_author_from_content(self, content: str) -> str:
        """Extract author information from content"""
        # Look for common author patterns
        author_patterns = [
            r'<meta\s+name=["\']author["\'][^>]*content=["\']([^"\']+)["\']',
            r'[Bb]y\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'[Aa]uthor[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]

        for pattern in author_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "Unknown Author"

    def _extract_date_from_content(self, content: str) -> datetime:
        """Extract publication date from content"""
        # Look for date patterns
        date_patterns = [
            r'<meta\s+name=["\']date["\'][^>]*content=["\']([^"\']+)["\']',
            r'<time[^>]*datetime=["\']([^"\']+)["\']',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                try:
                    # Try different date formats
                    for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%m/%d/%Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except ValueError:
                    continue

        return None

    def _create_excerpt(self, content: str, max_length: int = 300) -> str:
        """Create an excerpt from content"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', content)

        # Get first meaningful paragraph
        paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]

        if paragraphs:
            excerpt = paragraphs[0]
        else:
            # Fallback to first part of content
            excerpt = text.strip()

        # Truncate and add ellipsis
        if len(excerpt) > max_length:
            excerpt = excerpt[:max_length].rsplit(' ', 1)[0] + "..."

        return excerpt

    def _determine_source_type(self, url: str) -> str:
        """Determine source type from URL"""
        url_lower = url.lower()
        parsed = urlparse(url_lower)
        domain = parsed.netloc

        # Academic sources
        if any(pattern in domain for pattern in ['.edu', 'scholar.google', 'pubmed', 'arxiv', 'ieee', 'acm']):
            return "academic"

        # Government sources
        if any(pattern in domain for pattern in ['.gov', '.mil']):
            return "government"

        # News sources
        if any(pattern in domain for pattern in ['news', 'reuters', 'bbc', 'cnn', 'nytimes', 'guardian']):
            return "news"

        # Documentation
        if any(pattern in domain for pattern in ['docs.', 'documentation', 'github.com']):
            return "documentation"

        # Organization sources
        if any(pattern in domain for pattern in ['.org']):
            return "organization"

        return "web"

    async def _calculate_initial_reliability(self, content: PageContent) -> float:
        """Calculate initial reliability score based on content indicators"""
        score = 0.5

        # Content length factor
        if len(content.content) > 1000:
            score += 0.1

        # Presence of citations or references
        if any(pattern in content.content.lower() for pattern in ['reference', 'citation', 'source', 'bibliography']):
            score += 0.15

        # Structured content indicators
        if any(pattern in content.content for pattern in ['<h1>', '<h2>', '<ol>', '<ul>']):
            score += 0.1

        # Domain authority
        domain_score = self._calculate_domain_authority(content.url)
        score += domain_score * 0.25

        return min(1.0, score)

    def _calculate_domain_authority(self, url: str) -> float:
        """Calculate domain authority score (simplified)"""
        parsed = urlparse(url.lower())
        domain = parsed.netloc

        # High authority domains
        high_authority = [
            'wikipedia.org', 'stackoverflow.com', 'github.com',
            'mozilla.org', 'w3.org', 'ietf.org', 'rfc-editor.org'
        ]

        # Medium authority indicators
        medium_authority = ['.edu', '.gov', '.org']

        if any(ha in domain for ha in high_authority):
            return 0.9
        elif any(ma in domain for ma in medium_authority):
            return 0.7
        elif domain.count('.') == 1:  # Simple domain structure
            return 0.5
        else:
            return 0.3

    async def _analyze_content_quality(self, citation: Citation) -> float:
        """Analyze content quality using LLM"""
        if not citation.excerpt:
            return 0.3

        prompt = f"""
        Analyze the quality of this content excerpt for research purposes.
        Rate on a scale of 0.0 to 1.0 based on:
        - Factual content vs opinion
        - Presence of specific data or evidence
        - Professional tone and structure
        - Credibility indicators

        Content: {citation.excerpt}
        Source: {citation.url}

        Respond with just the numerical score:
        """

        try:
            response = await self.llm_adapter.clean_content(prompt, ContentType.TEXT)
            score = float(response.strip())
            return max(0.0, min(1.0, score))
        except Exception:
            return 0.5

    def _format_apa_citation(self, citation: Citation) -> str:
        """Format citation in APA style"""
        author = self._extract_author_from_content(citation.excerpt)
        year = citation.timestamp.year if citation.timestamp else datetime.now().year

        # Basic APA format: Author, A. A. (Year). Title. Website. URL
        if author and author != "Unknown Author":
            formatted = f"{author} ({year}). {citation.title}. "
        else:
            formatted = f"{citation.title}. ({year}). "

        # Add source information
        parsed = urlparse(citation.url)
        domain = parsed.netloc.replace('www.', '')
        formatted += f"{domain.title()}. "

        # Add URL
        formatted += f"Retrieved from {citation.url}"

        return formatted

    def _format_mla_citation(self, citation: Citation) -> str:
        """Format citation in MLA style"""
        author = self._extract_author_from_content(citation.excerpt)

        # Basic MLA format: Author. "Title." Website, Date, URL.
        if author and author != "Unknown Author":
            # Convert to Last, First format if possible
            parts = author.split()
            if len(parts) >= 2:
                author = f"{parts[-1]}, {' '.join(parts[:-1])}"
            formatted = f'{author}. '
        else:
            formatted = ""

        formatted += f'"{citation.title}." '

        # Add website name
        parsed = urlparse(citation.url)
        domain = parsed.netloc.replace('www.', '')
        formatted += f"{domain.title()}, "

        # Add date
        if citation.timestamp:
            formatted += f"{citation.timestamp.strftime('%d %b %Y')}, "

        # Add URL
        formatted += f"{citation.url}."

        return formatted

    def _format_chicago_citation(self, citation: Citation) -> str:
        """Format citation in Chicago style"""
        author = self._extract_author_from_content(citation.excerpt)

        # Basic Chicago format: Author. "Title." Website. Date. URL.
        if author and author != "Unknown Author":
            formatted = f"{author}. "
        else:
            formatted = ""

        formatted += f'"{citation.title}." '

        # Add website name
        parsed = urlparse(citation.url)
        domain = parsed.netloc.replace('www.', '')
        formatted += f"{domain.title()}. "

        # Add date
        if citation.timestamp:
            formatted += f"{citation.timestamp.strftime('%B %d, %Y')}. "

        # Add URL
        formatted += f"{citation.url}."

        return formatted
