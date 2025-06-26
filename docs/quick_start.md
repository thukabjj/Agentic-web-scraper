# 🚀 Quick Start

## Prerequisites
- Python 3.8 or higher
- Git (for cloning the repository)
- UV package manager (recommended)

## Installation

```bash
# Clone the repository
git clone https://github.com/thukabjj/Agentic-web-scraper.git
cd Agentic-web-scraper

# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate     # On Windows

# Install dependencies
uv pip install -r requirements.txt

# Install optional dependencies for dynamic content
playwright install chromium
```

## First Steps

```bash
# Run the test suite
uv run pytest tests/

# Start the server
uv run mcp_server.py

# Try a simple scrape
uv run mcp_server.py scrape-url "https://example.com"
```

For more details, see the [Usage Guide](usage.md) and [Troubleshooting](troubleshooting.md).
