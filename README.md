# Agentic Web Scraper with Deep Research

A sophisticated, production-ready **MCP (Model Context Protocol) Server** built on **hexagonal architecture** principles, featuring intelligent crawling, content analysis, and comprehensive **deep research capabilities**.

## 🔌 **MCP Server Capabilities**

This server implements the **Model Context Protocol** with support for both **STDIO** and **SSE** (Server-Sent Events) protocols, providing seamless integration with AI assistants and applications.

### 🚀 MCP Protocol Support

**Dual Protocol Implementation** - Choose the best protocol for your use case:

- **📡 MCP STDIO**: Direct stdin/stdout communication for local AI assistants (Claude Desktop, etc.)
- **🌐 MCP SSE**: Server-Sent Events for web-based AI applications and browser integration
- **🔧 Tool Integration**: Rich set of tools for web scraping and research across both protocols
- **📊 Structured Responses**: JSON, XML, and Markdown output formats on both STDIO and SSE
- **🤖 AI Assistant Ready**: Plug-and-play with Claude, ChatGPT, and other AI systems via either protocol

### 🛠️ MCP Tools Available

| Tool | Description | Protocol Support |
|------|-------------|------------------|
| `scrape_url` | Extract content from single URLs | STDIO, SSE |
| `scrape_multiple_urls` | Batch process multiple URLs | STDIO, SSE |
| `start_research` | Begin deep research project | STDIO, SSE |
| `research_interactive` | Interactive research session | STDIO, SSE |
| `list_research_projects` | List all research projects | STDIO, SSE |
| `export_research_report` | Generate research reports | STDIO, SSE |

## 🔬 **Deep Research Feature**

Transform your web scraping into intelligent research workflows with multi-stage analysis, evidence collection, source verification, and automated synthesis.

### ✨ Deep Research Capabilities

- **🎯 Multi-Stage Research**: Plan and execute comprehensive research workflows
- **📊 Evidence Collection**: Extract, analyze, and cross-reference evidence from multiple sources
- **🔍 Source Verification**: Automatically verify source reliability and authority
- **📚 Citation Management**: Generate proper citations in APA, MLA, and Chicago formats
- **🤖 AI-Powered Analysis**: Use local LLMs (Ollama) or cloud providers for intelligent analysis
- **📋 Research Reports**: Generate comprehensive markdown reports with bibliography
- **⚡ Interactive Research**: Real-time research sessions with evidence synthesis

## 🚀 Quick Start

### MCP Server Setup

**Both STDIO and SSE protocols are fully supported** for maximum compatibility with AI assistants and web applications.

#### STDIO Mode (Local AI Assistants)

```bash
# Clone and install
git clone https://github.com/your-org/agentic-web-scraper.git
cd agentic-web-scraper
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Run MCP server via STDIO
python mcp_server.py --stdio
```

#### SSE Mode (Web Applications)

```bash
# Run MCP server with SSE
python mcp_server.py --sse --port 8000 --host localhost

# Server available at: http://localhost:8000/sse
```

### Claude Desktop Integration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "agentic-web-scraper": {
      "command": "python",
      "args": ["path/to/agentic-web-scraper/mcp_server.py", "--stdio"],
      "env": {
        "PYTHONPATH": "path/to/agentic-web-scraper"
      }
    }
  }
}
```

### Basic Usage Examples

#### Simple Web Scraping via MCP

```python
# Via MCP tool call
{
  "tool": "scrape_url",
  "arguments": {
    "url": "https://example.com",
    "output_format": "markdown",
    "extract_links": true,
    "max_content_length": 10000
  }
}
```

#### Deep Research via MCP

```python
# Start research project
{
  "tool": "start_research",
  "arguments": {
    "research_question": "What are the latest trends in AI development?",
    "title": "AI Trends 2024 Research",
    "initial_urls": [
      "https://ai.google/research/",
      "https://openai.com/research/"
    ],
    "max_sources": 10,
    "include_contradictions": true
  }
}
```

#### Interactive Research Session

```python
# Interactive research
{
  "tool": "research_interactive",
  "arguments": {
    "question": "How does quantum computing impact cryptography?",
    "depth": "comprehensive",
    "format": "markdown"
  }
}
```

## 🏗️ Architecture Overview

### MCP Server Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │    │   Web Client     │    │   Local CLI     │
│   (Claude, etc) │    │   (Browser)      │    │   (Terminal)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
    MCP STDIO              MCP SSE               Direct Access
         │                       │                       │
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Server Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Tool Registry   │  │ Protocol        │  │ Response        │ │
│  │ & Validation    │  │ Handler         │  │ Formatter       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ CrawlSession    │  │ DeepResearch    │  │ Export          │ │
│  │ UseCase         │  │ UseCase         │  │ UseCase         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
┌─────────────────────────────────────────────────────────────────┐
│                      Domain Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ CrawlSession    │  │ ResearchProject │  │ Evidence        │ │
│  │ PageContent     │  │ ResearchStage   │  │ Citation        │ │
│  │ CrawlMetrics    │  │ Evidence Types  │  │ Research Status │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Web Adapters    │  │ LLM Adapters    │  │ Storage         │ │
│  │ • HTTP/Fetch    │  │ • Ollama        │  │ • JSON Files    │ │
│  │ • Playwright    │  │ • FastAgent     │  │ • Research DB   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📡 MCP Tool Reference

### Core Scraping Tools

#### `scrape_url`

Extract content from a single URL with intelligent parsing.

**Arguments:**

- `url` (string, required): Target URL to scrape
- `output_format` (string): "json" | "xml" | "markdown" (default: "json")
- `content_type` (string): "html" | "json" | "text" (default: "html")
- `extract_links` (boolean): Whether to extract page links (default: false)
- `max_content_length` (integer): Maximum content length to process

**Response:**

```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "title": "Example Domain",
    "content": "<!DOCTYPE html>...",
    "content_length": 1256,
    "quality_score": 0.85,
    "links": [...],
    "metadata": {
      "status_code": 200,
      "response_time_ms": 234,
      "fetch_timestamp": "2024-01-15T10:30:00Z"
    }
  }
}
```

#### `scrape_multiple_urls`

Batch process multiple URLs with concurrent execution.

**Arguments:**

- `urls` (array[string], required): List of URLs to scrape
- `output_format` (string): Output format for results
- `concurrent_limit` (integer): Max concurrent requests (default: 5)
- `timeout` (integer): Request timeout in seconds (default: 30)

### Research Tools

#### `start_research`

Begin a comprehensive research project with multi-stage analysis.

**Arguments:**

- `research_question` (string, required): Main research question
- `title` (string): Project title
- `description` (string): Project description
- `initial_urls` (array[string]): Starting URLs for research
- `max_sources` (integer): Maximum sources per stage (default: 8)
- `include_contradictions` (boolean): Include contradicting evidence (default: true)
- `citation_format` (string): "apa" | "mla" | "chicago" (default: "apa")

**Response:**

```json
{
  "success": true,
  "project": {
    "project_id": "proj_123456",
    "title": "AI Development Trends Research",
    "status": "completed",
    "confidence_level": 0.87,
    "evidence_count": 15,
    "stages_completed": 5,
    "findings": "Comprehensive research summary...",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### `research_interactive`

Conduct real-time interactive research with immediate results.

**Arguments:**

- `question` (string, required): Research question
- `depth` (string): "quick" | "standard" | "comprehensive" (default: "standard")
- `format` (string): Response format
- `max_sources` (integer): Sources to analyze

#### `list_research_projects`

List all research projects with metadata.

**Response:**

```json
{
  "success": true,
  "projects": [
    {
      "project_id": "proj_123",
      "title": "AI Trends Research",
      "status": "completed",
      "evidence_count": 15,
      "confidence_level": 0.87,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### `export_research_report`

Generate detailed research reports in various formats.

**Arguments:**

- `project_id` (string, required): Project to export
- `format` (string): "markdown" | "html" | "pdf" (default: "markdown")
- `include_bibliography` (boolean): Include citations (default: true)
- `include_evidence` (boolean): Include evidence details (default: true)

## 🔧 Configuration

### MCP Server Configuration

```python
# mcp_server.py configuration
MCP_CONFIG = {
    "server_name": "agentic-web-scraper",
    "version": "1.0.0",
    "protocols": ["stdio", "sse"],
    "tools": [
        "scrape_url",
        "scrape_multiple_urls",
        "start_research",
        "research_interactive",
        "list_research_projects",
        "export_research_report"
    ]
}
```

### Environment Variables

```bash
# Web scraping settings
export WEB_SCRAPER_USER_AGENT="Agentic-Web-Scraper/1.0"
export WEB_SCRAPER_TIMEOUT=30
export MAX_CONTENT_LENGTH=1048576

# MCP Server settings
export MCP_SERVER_HOST=localhost
export MCP_SERVER_PORT=8000
export MCP_ENABLE_CORS=true

# LLM settings
export LLM_PROVIDER=ollama
export LLM_MODEL=llama3
export LLM_BASE_URL=http://localhost:11434

# Research settings
export RESEARCH_MAX_SOURCES=10
export RESEARCH_MIN_EVIDENCE=3
export RESEARCH_AUTO_EXPAND=true
```

### Research Configuration

```python
from core.domain.models import ResearchConfig

config = ResearchConfig(
    max_sources_per_stage=10,        # Sources to analyze per stage
    min_evidence_threshold=5,        # Minimum evidence pieces required
    cross_reference_threshold=0.7,   # Similarity threshold for cross-referencing
    auto_expand_topics=True,         # Automatically discover related topics
    include_contradicting_evidence=True,  # Include conflicting evidence
    citation_format="apa",           # Bibliography format (apa, mla, chicago)
    max_research_depth=5             # Maximum research depth
)
```

## 🚀 AI Assistant Integration

### Claude Desktop

```json
{
  "mcpServers": {
    "agentic-web-scraper": {
      "command": "python",
      "args": ["mcp_server.py", "--stdio"],
      "env": {
        "PYTHONPATH": ".",
        "LLM_PROVIDER": "ollama"
      }
    }
  }
}
```

### ChatGPT Plugin

```json
{
  "name": "Agentic Web Scraper",
  "description": "Advanced web scraping and research capabilities",
  "mcp_endpoint": "http://localhost:8000/sse",
  "tools": ["scrape_url", "start_research", "research_interactive"]
}
```

### Custom Integration

```python
import asyncio
from mcp_client import MCPClient

async def use_research_tools():
    # Connect to MCP server
    client = MCPClient("stdio", command=["python", "mcp_server.py", "--stdio"])

    # Start research
    result = await client.call_tool("start_research", {
        "research_question": "What are the benefits of renewable energy?",
        "initial_urls": ["https://irena.org/", "https://www.iea.org/"],
        "max_sources": 8
    })

    print(f"Research completed: {result['project']['project_id']}")

    # Get detailed report
    report = await client.call_tool("export_research_report", {
        "project_id": result['project']['project_id'],
        "format": "markdown"
    })
```

## 📊 Usage Examples

### Academic Research via MCP

```python
# Research tool call
{
  "tool": "start_research",
  "arguments": {
    "research_question": "How is machine learning being applied in healthcare?",
    "title": "ML in Healthcare Research",
    "description": "Comprehensive analysis of ML applications in medical diagnosis and patient care",
    "initial_urls": [
      "https://www.nature.com/subjects/machine-learning",
      "https://pubmed.ncbi.nlm.nih.gov/",
      "https://www.nejm.org/"
    ],
    "max_sources": 12,
    "citation_format": "apa"
  }
}
```

### Market Research via MCP

```python
# Interactive research
{
  "tool": "research_interactive",
  "arguments": {
    "question": "What are the emerging trends in sustainable technology startups?",
    "depth": "comprehensive",
    "format": "markdown"
  }
}
```

### Technology Assessment

```python
# Multi-stage research
{
  "tool": "start_research",
  "arguments": {
    "research_question": "What are the current applications and limitations of blockchain technology?",
    "initial_urls": [
      "https://ethereum.org/",
      "https://bitcoin.org/",
      "https://hyperledger.org/"
    ],
    "include_contradictions": true,
    "max_sources": 15
  }
}
```

## 📈 Performance and Reliability

### MCP Protocol Performance

- **STDIO**: Direct process communication, minimal latency
- **SSE**: Web-compatible, supports real-time updates
- **Concurrent Processing**: Handle multiple tool calls simultaneously
- **Error Handling**: Robust error recovery and reporting

### Research Quality Metrics

- **Source Verification**: Domain authority and content quality assessment
- **Evidence Scoring**: Relevance and confidence metrics (0.0-1.0)
- **Cross-Reference Validation**: Multi-source verification
- **Contradiction Detection**: Identify conflicting information

### Scaling Considerations

- **Batch Processing**: Efficient handling of multiple URLs
- **Memory Management**: Optimized content processing
- **Rate Limiting**: Respectful crawling patterns
- **Caching**: Intelligent content and result caching

## 🔮 Advanced Features

### Custom Tool Development

```python
@mcp_tool("custom_research_tool")
async def custom_research(
    domain: str,
    focus_area: str,
    depth: int = 3
) -> Dict[str, Any]:
    """Custom research tool for specific domains"""
    # Implement custom research logic
    pass
```

### Research Workflow Automation

```python
# Automated research pipeline
{
  "tool": "start_research",
  "arguments": {
    "research_question": "AI safety measures in autonomous vehicles",
    "workflow": "academic",
    "auto_expand": true,
    "follow_citations": true,
    "verify_claims": true
  }
}
```

### Integration with Knowledge Graphs

```python
# Knowledge graph enhancement
{
  "tool": "research_with_kg",
  "arguments": {
    "question": "Climate change mitigation strategies",
    "kg_sources": ["wikidata", "dbpedia"],
    "relationship_depth": 2
  }
}
```

## 🛡️ Security and Privacy

### Data Protection

- **Local Processing**: Keep sensitive research data private
- **Configurable Storage**: Control where data is stored
- **Secure Communications**: Encrypted MCP protocol support
- **Access Controls**: Configurable tool access permissions

### Responsible Scraping

- **Rate Limiting**: Respect website resources
- **Robots.txt Compliance**: Honor site scraping policies
- **User Agent Identification**: Transparent scraping identification
- **Error Handling**: Graceful failure and retry logic

## 🤝 Contributing

We welcome contributions to enhance both MCP capabilities and research features:

1. **MCP Protocol**: Improve STDIO/SSE implementations
2. **Tool Development**: Add new research and scraping tools
3. **AI Integration**: Enhance assistant compatibility
4. **Research Algorithms**: Improve evidence analysis and synthesis
5. **Documentation**: Expand usage examples and guides

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🔌 Ready to integrate with your AI assistant? Connect via MCP STDIO or SSE and start intelligent research today! 🔬✨**
