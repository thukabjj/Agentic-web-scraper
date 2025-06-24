# Multi-stage build for agentic web scraper
FROM python:3.11-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt requirements-dev.txt ./

# Install dependencies into virtual environment
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install -r requirements.txt

# Install Playwright dependencies
RUN uv run playwright install-deps
RUN python -m playwright install chromium

# Production stage
FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy Playwright browsers
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data/sessions data/content

# Create non-root user
RUN useradd --create-home --shell /bin/bash scraper
RUN chown -R scraper:scraper /app
USER scraper

# Expose metrics port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default command
CMD ["python", "main.py", "config-info"]

# For running crawl tasks, override with:
# docker run agentic-scraper python main.py crawl https://example.com
