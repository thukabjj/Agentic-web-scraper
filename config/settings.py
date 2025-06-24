#!/usr/bin/env python3
"""
Configuration settings for the MCP Web Scraper
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class WebScraperSettings:
    """Configuration settings for the web scraper"""

    # Web scraping settings
    user_agent: str = "Agentic-Web-Scraper/1.0 (Educational Purpose)"
    timeout: int = 30
    max_redirects: int = 5
    max_content_length: int = 1048576  # 1MB

    # Performance settings
    concurrent_limit: int = 5
    request_delay: float = 1.0
    max_retries: int = 3

    # Storage settings
    storage_path: str = "./storage"

    # Observability settings
    enable_logging: bool = True
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "WebScraperSettings":
        """Create settings from environment variables"""
        return cls(
            user_agent=os.getenv("WEB_SCRAPER_USER_AGENT", cls.user_agent),
            timeout=int(os.getenv("WEB_SCRAPER_TIMEOUT", cls.timeout)),
            max_redirects=int(os.getenv("WEB_SCRAPER_MAX_REDIRECTS", cls.max_redirects)),
            max_content_length=int(os.getenv("MAX_CONTENT_LENGTH", cls.max_content_length)),
            concurrent_limit=int(os.getenv("CONCURRENT_LIMIT", cls.concurrent_limit)),
            request_delay=float(os.getenv("REQUEST_DELAY", cls.request_delay)),
            max_retries=int(os.getenv("MAX_RETRIES", cls.max_retries)),
            storage_path=os.getenv("STORAGE_PATH", cls.storage_path),
            enable_logging=os.getenv("OBSERVABILITY_ENABLE_LOGGING", "true").lower() == "true",
            log_level=os.getenv("OBSERVABILITY_LOG_LEVEL", cls.log_level)
        )


# Global settings instance
settings = WebScraperSettings.from_env()
