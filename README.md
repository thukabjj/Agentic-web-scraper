# Agentic Web Scraper

A high-precision, agent-driven web crawler that uses LLM, MCP, and Fetch MCP to extract main content and remove noise from web pages.

## Features
- **Automatic metrics generation by LLM**: The LLM analyzes the root page and generates a list of important page types, categories, or features to prioritize for crawling.
- **Page evaluation and selection based on metrics**: All URLs from the sitemap are evaluated (by LLM or rule) using the generated metrics, and only relevant pages are crawled.
- **LLM-powered cleaning**: Removes navigation, footers, ads, and other noise from Markdown content using LLM (no summarization, just noise removal).
- **Fetch MCP integration**: Robust content retrieval via MCP server.
- **Markdown output**: Clean, readable content saved as a single Markdown file.

## Prerequisites
- [uv](https://docs.astral.sh/uv/) and `uvx` must be available in your environment.
  - `uv` is a modern Python package manager and runner.
  - `uvx` allows running CLI tools (like `mcp-server-fetch`) without manual installation; uvx will fetch and run them automatically as needed.
- No need to manually install `mcp-server-fetch` or other MCP servers if using uv/uvx.

## Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/KunihiroS/Agentic-web-scraper.git
   cd Agentic-web-scraper
   ```
2. Install fast-agent-mcp and set up:
   ```bash
   uv pip install fast-agent-mcp
   uv fast-agent setup
   ```
3. Configure your MCP server and API keys as needed (see `fastagent.config.yaml`)
4. Run the crawler (specify the root URL as an argument or interactively):
   ```bash
   uv run agent.py https://fast-agent.ai/
   ```
5. The cleaned content will be saved to `site_crawl_result.md`

## Architecture
```mermaid
flowchart TD
    A["User provides root URL"] --> B["fetch_sitemap_urls: Get sitemap.xml"]
    B --> C["Extract all URLs"]
    C --> D["Fetch root page Markdown (content_fetcher_agent)"]
    D --> E["LLM generates evaluation metrics (metrics_generator_agent)"]
    E --> F["Evaluate all URLs with metrics (url_evaluator_agent)"]
    F --> G["For each selected URL, fetch Markdown (content_fetcher_agent)"]
    G --> H["LLM noise removal (content_cleaner_agent)"]
    H --> I["Save cleaned Markdown"]
    I --> J{"More URLs?"}
    J -- "Yes" --> G
    J -- "No" --> K["site_crawl_result.md complete"]
    style E fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
```

## Technology Stack
- [fast-agent](https://fast-agent.ai/) for agent orchestration and MCP integration
- [uv](https://docs.astral.sh/uv/) and `uvx` for dependency and CLI tool management

## License
MIT
