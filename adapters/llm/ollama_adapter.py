import asyncio
import json
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from core.domain.models import ContentType, CrawlMetrics, LLMConfig
from core.domain.ports import LLMPort


class OllamaAdapter(LLMPort):
    """Adapter for Ollama local LLM integration"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.base_url = config.base_url or "http://localhost:11434"
        self.model = config.model or "llama3"
        self.client = httpx.AsyncClient(timeout=config.timeout)

    async def generate_metrics(
        self, root_content: str, root_url: str
    ) -> CrawlMetrics:
        """Generate evaluation metrics from root page content"""
        prompt = f"""
        Based on the following website content, identify important keywords,
        patterns, and categories that should be prioritized for web crawling.

        Website: {root_url}
        Content: {root_content[:2000]}...

        Please extract:
        1. Important keywords (API, documentation, guide, tutorial, etc.)
        2. URL patterns that indicate valuable content
        3. Content categories that should be prioritized

        Return your response as JSON with this structure:
        {{
            "keywords": ["api", "documentation", "guide"],
            "patterns": ["/docs/", "/api/", "/tutorial/"],
            "categories": ["documentation", "api-reference", "guides"]
        }}
        """

        response = await self._generate_completion(prompt)

        try:
            # Try to parse JSON from response
            result = json.loads(response)
            return CrawlMetrics(
                keywords=result.get("keywords", []),
                patterns=result.get("patterns", []),
                categories=result.get("categories", []),
                generated_from_url=root_url
            )
        except json.JSONDecodeError:
            # Fallback to extracting from text
            return self._extract_metrics_from_text(response, root_url)

    async def extract_links(
        self, html_content: str, base_url: str
    ) -> List[str]:
        """Extract relevant links from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []

        # Extract all anchor tags
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']

            # Convert relative URLs to absolute
            if href.startswith('/'):
                full_url = urljoin(base_url, href)
            elif href.startswith('http'):
                full_url = href
            else:
                continue  # Skip other relative URLs for now

            # Only include links from the same domain
            if self._is_same_domain(full_url, base_url):
                links.append(full_url)

        # Use LLM to filter relevant links
        filtered_links = await self._filter_relevant_links(links, base_url)
        return list(set(filtered_links))  # Remove duplicates

    async def clean_content(
        self, content: str, content_type: ContentType
    ) -> str:
        """Clean and process page content to remove noise"""
        prompt = f"""
        Please clean the following {content_type.value} content by removing:
        - Navigation menus and headers
        - Footer content
        - Sidebar content
        - Advertisement blocks
        - Cookie notices
        - Social media widgets
        - Duplicate or redundant text

        Keep only the main content that would be valuable for documentation
        or reference purposes. Do NOT summarize - just remove noise.

        Content:
        {content[:4000]}...

        Return only the cleaned content:
        """

        return await self._generate_completion(prompt)

    async def evaluate_content_quality(
        self, content: str, url: str
    ) -> float:
        """Evaluate the quality of extracted content (0.0 to 1.0)"""
        prompt = f"""
        Rate the quality and usefulness of this content from {url}
        on a scale of 0.0 to 1.0, where:
        - 1.0 = Highly valuable documentation, API reference, or tutorial
        - 0.8 = Good quality technical content
        - 0.6 = Moderate quality content with some value
        - 0.4 = Basic content with limited value
        - 0.2 = Poor quality or mostly fluff content
        - 0.0 = No valuable content or error pages

        Content preview:
        {content[:1000]}...

        Respond with just the numerical score (e.g., 0.8):
        """

        response = await self._generate_completion(prompt)

        try:
            score = float(response.strip())
            return max(0.0, min(1.0, score))  # Clamp between 0.0 and 1.0
        except ValueError:
            return 0.5  # Default middle score if parsing fails

    async def _generate_completion(self, prompt: str) -> str:
        """Generate completion using Ollama API"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")

    async def _filter_relevant_links(
        self, links: List[str], base_url: str
    ) -> List[str]:
        """Use LLM to filter relevant links"""
        if len(links) <= 20:
            return links  # Don't filter small lists

        links_text = '\n'.join(links[:50])  # Limit for prompt size

        prompt = f"""
        From this list of URLs from {base_url}, select only those that
        likely contain valuable documentation, API references, guides,
        tutorials, or other important technical content.

        Skip URLs that appear to be:
        - Navigation or menu items
        - Footer links
        - Social media links
        - Contact/About pages
        - Generic landing pages

        URLs:
        {links_text}

        Return only the valuable URLs, one per line:
        """

        response = await self._generate_completion(prompt)

        # Extract URLs from response
        filtered = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('http') and line in links:
                filtered.append(line)

        return filtered if filtered else links[:20]  # Fallback

    def _extract_metrics_from_text(
        self, text: str, root_url: str
    ) -> CrawlMetrics:
        """Extract metrics from unstructured text response"""
        # Basic keyword extraction as fallback
        common_keywords = [
            "api", "documentation", "docs", "guide", "tutorial",
            "reference", "help", "getting-started", "quickstart"
        ]

        text_lower = text.lower()
        found_keywords = [
            kw for kw in common_keywords
            if kw in text_lower
        ]

        return CrawlMetrics(
            keywords=found_keywords or ["documentation"],
            patterns=["/docs/", "/api/", "/guide/"],
            categories=["documentation"],
            generated_from_url=root_url,
            confidence_score=0.5  # Lower confidence for fallback
        )

    def _is_same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs are from the same domain"""
        try:
            domain1 = urlparse(url1).netloc
            domain2 = urlparse(url2).netloc
            return domain1 == domain2
        except Exception:
            return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    # New research-specific methods
    async def generate_research_queries(
        self,
        research_question: str,
        context: str = ""
    ) -> List[str]:
        """Generate search queries for research"""
        prompt = f"""
        Generate 5-7 specific search queries to thoroughly research this question:
        "{research_question}"

        {f"Additional context: {context}" if context else ""}

        Create queries that:
        1. Cover different aspects of the question
        2. Include related terms and synonyms
        3. Target specific domains or types of sources
        4. Range from broad to specific

        Return each query on a new line, without numbering:
        """

        response = await self._generate_completion(prompt)

        # Parse queries from response
        queries = []
        for line in response.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                # Remove bullet points, numbers, etc.
                clean_query = line.lstrip('•-*123456789. ')
                if clean_query:
                    queries.append(clean_query)

        return queries[:7]  # Limit to 7 queries

    async def analyze_research_relevance(
        self,
        content: str,
        research_question: str
    ) -> float:
        """Analyze how relevant content is to research question"""
        prompt = f"""
        Rate how relevant this content is to the research question on a scale of 0.0 to 1.0.

        Research Question: {research_question}

        Content: {content[:2000]}...

        Consider:
        - Direct relevance to the question
        - Quality of information provided
        - Specific vs general information
        - Credibility of claims made

        Respond with just the numerical score (e.g., 0.85):
        """

        response = await self._generate_completion(prompt)

        try:
            score = float(response.strip())
            return max(0.0, min(1.0, score))
        except ValueError:
            return 0.5

    async def extract_key_claims(
        self,
        content: str
    ) -> List[str]:
        """Extract key claims from content"""
        prompt = f"""
        Extract 3-5 key factual claims or findings from this content.
        Focus on specific, verifiable statements rather than opinions.

        Content: {content[:3000]}...

        Return each claim on a new line, without numbering:
        """

        response = await self._generate_completion(prompt)

        # Parse claims from response
        claims = []
        for line in response.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 20:
                # Remove bullet points, numbers, etc.
                clean_claim = line.lstrip('•-*123456789. ')
                if clean_claim:
                    claims.append(clean_claim)

        return claims[:5]  # Limit to 5 claims

    async def generate_research_summary(
        self,
        evidence_list: List["Evidence"],
        research_question: str
    ) -> str:
        """Generate a research summary from evidence"""
        if not evidence_list:
            return "No evidence available for analysis."

        # Organize evidence by type
        evidence_by_type = {}
        for evidence in evidence_list:
            etype = evidence.evidence_type.value
            if etype not in evidence_by_type:
                evidence_by_type[etype] = []
            evidence_by_type[etype].append(evidence.content[:300])

        # Create evidence summary
        evidence_summary = ""
        for etype, contents in evidence_by_type.items():
            evidence_summary += f"\n{etype.title()} Evidence:\n"
            for i, content in enumerate(contents[:3], 1):  # Limit for prompt size
                evidence_summary += f"{i}. {content}...\n"

        prompt = f"""
        Based on the following evidence, provide a comprehensive research summary
        addressing this question: "{research_question}"

        Evidence collected:
        {evidence_summary}

        Provide a summary that:
        1. Directly addresses the research question
        2. Synthesizes findings from different sources
        3. Notes any contradictions or uncertainties
        4. Draws evidence-based conclusions
        5. Identifies areas needing further research

        Structure your response with clear sections and cite the evidence types used.
        """

        return await self._generate_completion(prompt)
