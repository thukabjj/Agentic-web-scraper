from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CrawlStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"


class UrlScore(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ContentType(str, Enum):
    HTML = "html"
    TEXT = "text"
    JSON = "json"


@dataclass
class CrawlTarget:
    """Represents a URL to be crawled"""
    url: str
    content_type: ContentType = ContentType.HTML
    max_depth: int = 1
    follow_external: bool = False


@dataclass
class PageContent:
    """Represents the content extracted from a web page"""
    url: str
    content: str
    content_type: ContentType
    timestamp: datetime = None
    title: Optional[str] = None
    status_code: int = 200
    headers: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.headers is None:
            self.headers = {}


@dataclass
class CrawlMetrics:
    """Metrics generated for evaluating URL importance"""
    keywords: List[str]
    patterns: List[str]
    categories: List[str]
    generated_from_url: str
    confidence_score: float = 0.8
    generated_at: datetime = None

    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.utcnow()


@dataclass
class CrawlSession:
    """Represents a crawling session"""
    session_id: str
    name: str
    targets: List[CrawlTarget]
    status: CrawlStatus = CrawlStatus.PENDING
    created_at: datetime = None
    pages_crawled: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


# Pydantic models for configuration and API
class LLMConfig(BaseModel):
    provider: str = Field(
        default="anthropic",
        description="LLM provider (anthropic, openai, ollama)"
    )
    model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Model identifier"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for external providers"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Base URL for local providers like Ollama"
    )
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, gt=0)
    timeout: int = Field(default=30, gt=0)


class ObservabilityConfig(BaseModel):
    enable_logging: bool = True
    enable_metrics: bool = True
    enable_tracing: bool = True
    log_level: str = "INFO"
    metrics_port: int = 8000
    jaeger_endpoint: Optional[str] = None


class CrawlConfig(BaseModel):
    max_concurrent_requests: int = Field(default=5, gt=0, le=20)
    request_delay: float = Field(default=1.0, ge=0.0)
    max_retries: int = Field(default=3, ge=0)
    timeout: int = Field(default=30, gt=0)
    user_agent: str = (
        "Mozilla/5.0 (compatible; AgenticWebScraper/1.0)"
    )
    respect_robots_txt: bool = True


class ScraperConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    crawl: CrawlConfig = Field(default_factory=CrawlConfig)
    observability: ObservabilityConfig = Field(
        default_factory=ObservabilityConfig
    )
    output_format: str = "markdown"
    resume_enabled: bool = True
    interactive_mode: bool = True


# Export format for results
class ExportFormat(str, Enum):
    JSON = "json"
    XML = "xml"
    MARKDOWN = "markdown"


# Deep Research Models
class ResearchStatus(str, Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class EvidenceType(str, Enum):
    PRIMARY = "primary"        # Original sources, documents
    SECONDARY = "secondary"    # Analysis, commentary
    SUPPORTING = "supporting"  # Additional context
    CONTRADICTING = "contradicting"  # Counter-evidence


class ResearchStageType(str, Enum):
    INITIAL_SEARCH = "initial_search"
    SOURCE_VERIFICATION = "source_verification"
    DEEP_DIVE = "deep_dive"
    CROSS_REFERENCE = "cross_reference"
    SYNTHESIS = "synthesis"
    CITATION_CHECK = "citation_check"


@dataclass
class Citation:
    """Represents a source citation with metadata"""
    url: str
    title: str
    excerpt: str
    timestamp: datetime
    source_type: str = "web"  # web, academic, news, docs
    reliability_score: float = 0.8
    page_content_id: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)


@dataclass
class Evidence:
    """Represents a piece of evidence supporting or contradicting a claim"""
    content: str
    evidence_type: EvidenceType
    citation: Citation
    relevance_score: float = 0.8
    confidence_score: float = 0.8
    extracted_at: datetime = None
    tags: List[str] = None

    def __post_init__(self):
        if self.extracted_at is None:
            self.extracted_at = datetime.now()
        if self.tags is None:
            self.tags = []


@dataclass
class ResearchStage:
    """Represents a stage in the research process"""
    stage_id: str
    stage_type: ResearchStageType
    description: str
    status: ResearchStatus = ResearchStatus.PLANNING
    queries: List[str] = None
    targets: List[CrawlTarget] = None
    evidence_collected: List[Evidence] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    next_stages: List[str] = None  # IDs of follow-up stages

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.queries is None:
            self.queries = []
        if self.targets is None:
            self.targets = []
        if self.evidence_collected is None:
            self.evidence_collected = []
        if self.next_stages is None:
            self.next_stages = []


@dataclass
class ResearchProject:
    """Represents a comprehensive research project"""
    project_id: str
    title: str
    research_question: str
    description: str
    status: ResearchStatus = ResearchStatus.PLANNING
    stages: List[ResearchStage] = None
    all_evidence: List[Evidence] = None
    findings: str = ""
    conclusions: str = ""
    confidence_level: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None
    tags: List[str] = None
    related_projects: List[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.stages is None:
            self.stages = []
        if self.all_evidence is None:
            self.all_evidence = []
        if self.tags is None:
            self.tags = []
        if self.related_projects is None:
            self.related_projects = []


class ResearchConfig(BaseModel):
    max_sources_per_stage: int = Field(default=10, gt=0, le=50)
    min_evidence_threshold: int = Field(default=3, gt=0)
    cross_reference_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    auto_expand_topics: bool = True
    include_contradicting_evidence: bool = True
    citation_format: str = "apa"  # apa, mla, chicago
    max_research_depth: int = Field(default=5, gt=0, le=10)
