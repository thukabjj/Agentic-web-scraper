# 📚 Usage Guide

## CLI Usage

Start the server in CLI mode:

```bash
uv run mcp_server.py --cli
```

Available commands:

- `scrape <url> [--output-format ...] [--content-type ...] [--extract-links] [--max-content-length N]`
- `analyze <url> <question> [--output-format ...] [--content-type ...] [--extract-links]`
- `research <question>`
- `help`
- `quit`

**Example:**

```bash
scrape https://finance.yahoo.com/quote/%5EGSPC/ --output-format json --content-type html --extract-links --max-content-length 10000
analyze https://finance.yahoo.com/quote/%5EGSPC/ "What is the current S&P 500 value?" --output-format json --content-type html --extract-links
```

## Python API Usage

```python
from improved_test import ImprovedAnalyzer

async def scrape_basic():
    analyzer = ImprovedAnalyzer()
    result = await analyzer.scrape("https://example.com")
    print(result)

async def analyze_content():
    analyzer = ImprovedAnalyzer()
    result = await analyzer.analyze(
        url="https://example.com",
        question="What are the main topics?"
    )
    print(result['response'])
```

## Common Use Cases

- Simple web scraping
- Financial data analysis
- Research projects
- Batch processing multiple URLs
- Scraping with authentication

For more advanced features, see [Advanced Features](advanced.md). For troubleshooting, see [Troubleshooting](troubleshooting.md).
