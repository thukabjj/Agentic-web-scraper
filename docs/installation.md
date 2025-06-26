# 📥 Installation Guide

## System Requirements
- **Python**: Version 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM recommended
- **Storage**: At least 1GB free space

## Package Manager Setup

We recommend using UV for faster and more reliable package management:

```bash
# Install UV on Unix/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install UV on Windows PowerShell
(Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -UseBasicParsing).Content | pwsh -Command -

# Verify installation
uv --version
```

## Environment Setup

1. **Create Project Directory**
```bash
git clone https://github.com/thukabjj/Agentic-web-scraper.git
cd Agentic-web-scraper
```

2. **Virtual Environment**
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate     # On Windows
```

3. **Install Dependencies**
```bash
uv pip install -r requirements.txt
playwright install chromium  # For dynamic content support
```

## Configuration

1. **Environment Variables**
Create a `.env` file in the project root:
```bash
# Required for AI functionality
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here

# Optional: Custom endpoints
OLLAMA_BASE_URL=http://localhost:11434/api
```

2. **Verify Installation**
```bash
uv run pytest tests/
uv run mcp_server.py
```

For a quick overview, see the [Quick Start](quick_start.md). For troubleshooting, see [Troubleshooting](troubleshooting.md).
