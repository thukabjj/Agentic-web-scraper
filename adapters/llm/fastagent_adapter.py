import json
from typing import List
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from mcp_agent.core.fastagent import FastAgent

from core.domain.models import ContentType, CrawlMetrics, LLMConfig
from core.domain.ports import LLMPort


class FastAgentAdapter(LLMPort):
    """Adapter for FastAgent MCP integration"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.agent = FastAgent("WebScraperAgent")
        self._setup_agents()

    def _setup_agents(self):
        """Setup FastAgent agents"""

        @self.agent.agent(
            "metrics_generator_agent",
            instruction="""Given the full content of a website's root page
            (Markdown or HTML), extract a list of important page types,
            categories, or features that should be prioritized for crawling
            (e.g., API reference, documentation, tutorials, release notes, etc).
            Return a Python list of keywords or patterns that can be used to
            evaluate the importance of URLs in the sitemap."""
        )
        async def metrics_generator_agent(agent, root_content: str):
            pass

        @self.agent.agent(
            "link_extractor_agent",
            instruction="""Given the raw HTML of a web page, extract all
            unique internal links (absolute URLs within the same domain) that
            are likely to be important for crawling (e.g., documentation,
            guides, API, tutorials, etc). Return a Python list of URLs as
            strings. Do not include navigation, footer, or external links."""
        )
        async def link_extractor_agent(agent, html: str, base_url: str):
            pass

        @self.agent.agent(
            "content_cleaner_agent",
            instruction="""Given the Markdown content of a web page, remove
            navigation, footer, sidebar, ads, duplicated explanations, and
            error messages. Do NOT summarize or rewrite the content, just
            remove obvious noise and keep the main text as Markdown. Return
            only the cleaned Markdown."""
        )
        async def content_cleaner_agent(agent, markdown: str):
            pass

        @self.agent.agent(
            "content_evaluator_agent",
            instruction="""Evaluate the quality and usefulness of this content
            on a scale of 0.0 to 1.0. Consider factors like completeness,
            technical depth, and relevance. Return only the numerical score."""
        )
        async def content_evaluator_agent(agent, content: str, url: str):
            pass

    async def generate_metrics(
        self, root_content: str, root_url: str
    ) -> CrawlMetrics:
        """Generate evaluation metrics from root page content"""
        async with self.agent.run() as agent:
            metrics_data = await agent.metrics_generator_agent(root_content)

            # Parse the response - it should be a list of keywords/patterns
            if isinstance(metrics_data, list):
                keywords = metrics_data
            else:
                # Try to extract from string response
                keywords = self._extract_keywords_from_text(str(metrics_data))

            # Generate patterns from keywords
            patterns = [f"/{kw}/" for kw in keywords if len(kw) > 2]

            return CrawlMetrics(
                keywords=keywords,
                patterns=patterns,
                categories=keywords,  # Use keywords as categories
                generated_from_url=root_url
            )

    async def extract_links(
        self, html_content: str, base_url: str
    ) -> List[str]:
        """Extract relevant links from HTML content"""
        async with self.agent.run() as agent:
            links = await agent.link_extractor_agent(html_content, base_url)

            if isinstance(links, list):
                return links
            elif isinstance(links, str):
                # Try to parse as list or extract URLs
                return self._extract_urls_from_text(links, base_url)
            else:
                return []

    async def clean_content(
        self, content: str, content_type: ContentType
    ) -> str:
        """Clean and process page content to remove noise"""
        async with self.agent.run() as agent:
            cleaned = await agent.content_cleaner_agent(content)
            return str(cleaned) if cleaned else content

    async def evaluate_content_quality(
        self, content: str, url: str
    ) -> float:
        """Evaluate the quality of extracted content (0.0 to 1.0)"""
        async with self.agent.run() as agent:
            try:
                score = await agent.content_evaluator_agent(content, url)
                if isinstance(score, (int, float)):
                    return max(0.0, min(1.0, float(score)))
                elif isinstance(score, str):
                    return max(0.0, min(1.0, float(score.strip())))
                else:
                    return 0.5
            except (ValueError, TypeError):
                return 0.5

    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text response"""
        # Try to find list-like patterns
        keywords = []

        # Look for Python list format
        if '[' in text and ']' in text:
            try:
                # Extract content between brackets
                start = text.find('[')
                end = text.find(']', start) + 1
                list_str = text[start:end]
                keywords = eval(list_str)  # Note: eval is dangerous in production
                if isinstance(keywords, list):
                    return [str(k).strip(' "\'') for k in keywords]
            except:
                pass

        # Fallback: look for common patterns
        common_patterns = [
            "api", "documentation", "docs", "guide", "tutorial",
            "reference", "help", "getting-started", "quickstart",
            "examples", "changelog", "release", "faq"
        ]

        text_lower = text.lower()
        return [p for p in common_patterns if p in text_lower]

    def _extract_urls_from_text(
        self, text: str, base_url: str
    ) -> List[str]:
        """Extract URLs from text response"""
        urls = []
        base_domain = urlparse(base_url).netloc

        # Split by lines and look for URLs
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('http'):
                # Check if it's from the same domain
                try:
                    if urlparse(line).netloc == base_domain:
                        urls.append(line)
                except:
                    continue

        return urls

    # New research-specific methods
    async def generate_research_queries(
        self,
        research_question: str,
        context: str = ""
    ) -> List[str]:
        """Generate search queries for research using FastAgent"""

        @self.agent.agent(
            "research_query_generator",
            instruction=f"""Generate 5-7 specific search queries to research: {research_question}
            {f"Context: {context}" if context else ""}
            Return a Python list of query strings."""
        )
        async def generate_queries_agent(agent, question: str):
            pass

        async with self.agent.run() as agent:
            queries = await agent.research_query_generator(research_question)

            if isinstance(queries, list):
                return queries[:7]
            else:
                # Fallback parsing
                return self._parse_queries_from_text(str(queries))

    async def analyze_research_relevance(
        self,
        content: str,
        research_question: str
    ) -> float:
        """Analyze research relevance using FastAgent"""

        @self.agent.agent(
            "relevance_analyzer",
            instruction=f"""Rate content relevance to research question: {research_question}
            Return a score between 0.0 and 1.0."""
        )
        async def analyze_relevance_agent(agent, content_text: str):
            pass

        async with self.agent.run() as agent:
            try:
                score = await agent.relevance_analyzer(content[:2000])
                return max(0.0, min(1.0, float(score)))
            except (ValueError, TypeError):
                return 0.5

    async def extract_key_claims(
        self,
        content: str
    ) -> List[str]:
        """Extract key claims using FastAgent"""

        @self.agent.agent(
            "claims_extractor",
            instruction="""Extract 3-5 key factual claims from content.
            Return a Python list of claim strings."""
        )
        async def extract_claims_agent(agent, content_text: str):
            pass

        async with self.agent.run() as agent:
            claims = await agent.extract_claims_agent(content[:3000])

            if isinstance(claims, list):
                return claims[:5]
            else:
                return self._parse_claims_from_text(str(claims))

    async def generate_research_summary(
        self,
        evidence_list: List["Evidence"],
        research_question: str
    ) -> str:
        """Generate research summary using FastAgent"""
        if not evidence_list:
            return "No evidence available for analysis."

        # Prepare evidence summary
        evidence_text = ""
        for i, evidence in enumerate(evidence_list[:10], 1):  # Limit for prompt
            evidence_text += f"{i}. {evidence.content[:200]}...\n"

        @self.agent.agent(
            "research_summarizer",
            instruction=f"""Create a comprehensive research summary addressing: {research_question}
            Based on the provided evidence, synthesize findings and draw conclusions."""
        )
        async def summarize_research_agent(agent, evidence_data: str):
            pass

        async with self.agent.run() as agent:
            summary = await agent.summarize_research_agent(evidence_text)
            return str(summary) if summary else "Unable to generate summary."

    def _parse_queries_from_text(self, text: str) -> List[str]:
        """Parse queries from text response"""
        queries = []

        # Try to find list-like patterns
        if '[' in text and ']' in text:
            try:
                start = text.find('[')
                end = text.find(']', start) + 1
                list_str = text[start:end]
                parsed = eval(list_str)  # Note: eval is dangerous in production
                if isinstance(parsed, list):
                    return [str(q).strip(' "\'') for q in parsed][:7]
            except:
                pass

        # Fallback: split by lines
        for line in text.split('\n'):
            line = line.strip()
            if line and len(line) > 10:
                clean_query = line.lstrip('•-*123456789. ')
                if clean_query:
                    queries.append(clean_query)

        return queries[:7]

    def _parse_claims_from_text(self, text: str) -> List[str]:
        """Parse claims from text response"""
        claims = []

        # Similar logic to query parsing
        if '[' in text and ']' in text:
            try:
                start = text.find('[')
                end = text.find(']', start) + 1
                list_str = text[start:end]
                parsed = eval(list_str)
                if isinstance(parsed, list):
                    return [str(c).strip(' "\'') for c in parsed][:5]
            except:
                pass

        # Fallback parsing
        for line in text.split('\n'):
            line = line.strip()
            if line and len(line) > 20:
                clean_claim = line.lstrip('•-*123456789. ')
                if clean_claim:
                    claims.append(clean_claim)

        return claims[:5]
