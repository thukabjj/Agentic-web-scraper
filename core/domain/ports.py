from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .models import (Citation, ContentType, CrawlMetrics, CrawlSession,
                     Evidence, PageContent, ResearchProject, ResearchStage)


class WebAdapterPort(ABC):
    """Port for web content fetching"""

    @abstractmethod
    async def fetch_content(
        self,
        url: str,
        content_type: ContentType = ContentType.HTML
    ) -> Optional[PageContent]:
        """Fetch content from a URL"""
        pass

    @abstractmethod
    async def fetch_multiple(
        self,
        urls: List[str],
        content_type: ContentType = ContentType.HTML
    ) -> List[Optional[PageContent]]:
        """Fetch content from multiple URLs"""
        pass

    @abstractmethod
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        pass

    @abstractmethod
    async def get_page_links(self, url: str) -> List[str]:
        """Extract links from a webpage"""
        pass


class StorageAdapterPort(ABC):
    """Port for data persistence"""

    @abstractmethod
    async def save_session(self, session: CrawlSession) -> None:
        """Save crawl session"""
        pass

    @abstractmethod
    async def load_session(self, session_id: str) -> Optional[CrawlSession]:
        """Load crawl session by ID"""
        pass

    @abstractmethod
    async def save_content(self, content: PageContent) -> None:
        """Save page content"""
        pass

    @abstractmethod
    async def export_to_file(self, data: Any, filepath: str) -> None:
        """Export data to file"""
        pass


class LoggingPort(ABC):
    """Port for structured logging"""

    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        pass

    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        pass

    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        pass


class ConfigurationPort(ABC):
    """Port for configuration management"""

    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate current configuration"""
        pass


# Deep Research Ports
class ResearchPort(ABC):
    """Port for managing research projects and workflows"""

    @abstractmethod
    async def create_research_project(
        self,
        title: str,
        research_question: str,
        description: str = ""
    ) -> ResearchProject:
        """Create a new research project"""
        pass

    @abstractmethod
    async def plan_research_stages(
        self,
        project: ResearchProject
    ) -> List[ResearchStage]:
        """Plan the stages for a research project"""
        pass

    @abstractmethod
    async def execute_research_stage(
        self,
        project: ResearchProject,
        stage: ResearchStage
    ) -> ResearchStage:
        """Execute a specific research stage"""
        pass

    @abstractmethod
    async def synthesize_findings(
        self,
        project: ResearchProject
    ) -> str:
        """Synthesize all research findings into conclusions"""
        pass


class EvidenceAnalysisPort(ABC):
    """Port for analyzing and validating evidence"""

    @abstractmethod
    async def extract_evidence(
        self,
        content: PageContent,
        research_context: str
    ) -> List[Evidence]:
        """Extract relevant evidence from page content"""
        pass

    @abstractmethod
    async def cross_reference_evidence(
        self,
        evidence_list: List[Evidence],
        threshold: float = 0.7
    ) -> Dict[str, List[Evidence]]:
        """Cross-reference evidence to find supporting/contradicting claims"""
        pass

    @abstractmethod
    async def evaluate_evidence_quality(
        self,
        evidence: Evidence
    ) -> float:
        """Evaluate the quality and reliability of evidence"""
        pass

    @abstractmethod
    async def detect_contradictions(
        self,
        evidence_list: List[Evidence]
    ) -> List[Dict[str, Any]]:
        """Detect contradictory evidence"""
        pass


class CitationPort(ABC):
    """Port for managing citations and source tracking"""

    @abstractmethod
    async def generate_citation(
        self,
        content: PageContent,
        citation_format: str = "apa"
    ) -> Citation:
        """Generate a properly formatted citation"""
        pass

    @abstractmethod
    async def verify_source_reliability(
        self,
        citation: Citation
    ) -> float:
        """Verify the reliability of a source"""
        pass

    @abstractmethod
    async def format_bibliography(
        self,
        citations: List[Citation],
        format_style: str = "apa"
    ) -> str:
        """Format a bibliography from citations"""
        pass


class LLMPort(ABC):
    """Enhanced LLM port with research capabilities"""

    @abstractmethod
    async def generate_metrics(
        self, root_content: str, root_url: str
    ) -> CrawlMetrics:
        """Generate evaluation metrics from root page content"""
        pass

    @abstractmethod
    async def extract_links(
        self, html_content: str, base_url: str
    ) -> List[str]:
        """Extract relevant links from HTML content"""
        pass

    @abstractmethod
    async def clean_content(
        self, content: str, content_type: ContentType
    ) -> str:
        """Clean and process page content to remove noise"""
        pass

    @abstractmethod
    async def evaluate_content_quality(
        self, content: str, url: str
    ) -> float:
        """Evaluate the quality of extracted content (0.0 to 1.0)"""
        pass

    # New research-specific methods
    @abstractmethod
    async def generate_research_queries(
        self,
        research_question: str,
        context: str = ""
    ) -> List[str]:
        """Generate search queries for research"""
        pass

    @abstractmethod
    async def analyze_research_relevance(
        self,
        content: str,
        research_question: str
    ) -> float:
        """Analyze how relevant content is to research question"""
        pass

    @abstractmethod
    async def extract_key_claims(
        self,
        content: str
    ) -> List[str]:
        """Extract key claims from content"""
        pass

    @abstractmethod
    async def generate_research_summary(
        self,
        evidence_list: List[Evidence],
        research_question: str
    ) -> str:
        """Generate a research summary from evidence"""
        pass
