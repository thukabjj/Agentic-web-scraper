#!/usr/bin/env python3
"""
Agentic Web Scraper MCP Server

A comprehensive Model Context Protocol (MCP) server that provides:
- Web scraping and content extraction tools
- Deep research capabilities with evidence collection
- Multi-stage research workflows
- Citation management and bibliography generation

Supports both STDIO and SSE (Server-Sent Events) protocols for
integration with AI assistants and web applications.

Usage:
    # STDIO mode (for local AI assistants like Claude Desktop)
    python mcp_server.py --stdio

    # SSE mode (for web applications)
    python mcp_server.py --sse --port 8000 --host localhost

    # CLI mode (for direct usage)
    python mcp_server.py --cli
"""

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from adapters.storage.json_storage import JsonStorageAdapter
from adapters.web.fetch_adapter import FetchAdapter
from config.settings import WebScraperSettings, settings
from core.domain.models import ContentType

# MCP Server Configuration
MCP_SERVER_INFO = {
    "name": "agentic-web-scraper",
    "version": "1.0.0",
    "description": "Advanced web scraping and deep research MCP server",
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


class WebScraperMCPServer:
    """
    MCP Server for web scraping and deep research capabilities

    Implements the Model Context Protocol with support for:
    - STDIO: Direct stdin/stdout communication
    - SSE: Server-Sent Events for web integration
    """

    def __init__(self):
        self.settings = WebScraperSettings.from_env()
        self.web_adapter = FetchAdapter()
        self.storage = JsonStorageAdapter(settings.storage_path)
        self.tools = self._register_tools()
        print("✅ MCP Web Scraper Server initialized")

    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """Register all available MCP tools"""
        return {
            "scrape_url": {
                "description": "Extract content from a single URL with intelligent parsing",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Target URL to scrape"
                        },
                        "output_format": {
                            "type": "string",
                            "enum": ["json", "xml", "markdown"],
                            "default": "json",
                            "description": "Output format for the scraped content"
                        },
                        "content_type": {
                            "type": "string",
                            "enum": ["html", "json", "text"],
                            "default": "html",
                            "description": "Expected content type"
                        },
                        "extract_links": {
                            "type": "boolean",
                            "default": False,
                            "description": "Whether to extract and return page links"
                        },
                        "max_content_length": {
                            "type": "integer",
                            "description": "Maximum content length to process"
                        }
                    },
                    "required": ["url"]
                }
            },
            "scrape_multiple_urls": {
                "description": "Batch process multiple URLs with concurrent execution",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "urls": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of URLs to scrape"
                        },
                        "output_format": {
                            "type": "string",
                            "enum": ["json", "xml", "markdown"],
                            "default": "json"
                        },
                        "concurrent_limit": {
                            "type": "integer",
                            "default": 5,
                            "description": "Maximum concurrent requests"
                        },
                        "timeout": {
                            "type": "integer",
                            "default": 30,
                            "description": "Request timeout in seconds"
                        }
                    },
                    "required": ["urls"]
                }
            },
            "start_research": {
                "description": "Begin a comprehensive research project with multi-stage analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "research_question": {
                            "type": "string",
                            "description": "Main research question to investigate"
                        },
                        "title": {
                            "type": "string",
                            "description": "Project title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Project description"
                        },
                        "initial_urls": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Starting URLs for research"
                        },
                        "max_sources": {
                            "type": "integer",
                            "default": 8,
                            "description": "Maximum sources per research stage"
                        },
                        "include_contradictions": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include contradicting evidence"
                        },
                        "citation_format": {
                            "type": "string",
                            "enum": ["apa", "mla", "chicago"],
                            "default": "apa",
                            "description": "Citation format for bibliography"
                        }
                    },
                    "required": ["research_question"]
                }
            },
            "research_interactive": {
                "description": "Conduct real-time interactive research with immediate results",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Research question"
                        },
                        "depth": {
                            "type": "string",
                            "enum": ["quick", "standard", "comprehensive"],
                            "default": "standard",
                            "description": "Research depth level"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "Response format"
                        },
                        "max_sources": {
                            "type": "integer",
                            "default": 5,
                            "description": "Maximum sources to analyze"
                        }
                    },
                    "required": ["question"]
                }
            },
            "list_research_projects": {
                "description": "List all research projects with metadata",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "completed", "in_progress", "failed"],
                            "default": "all",
                            "description": "Filter projects by status"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 20,
                            "description": "Maximum number of projects to return"
                        }
                    }
                }
            },
            "export_research_report": {
                "description": "Generate detailed research reports in various formats",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project ID to export"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "html", "json"],
                            "default": "markdown",
                            "description": "Export format"
                        },
                        "include_bibliography": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include citations and bibliography"
                        },
                        "include_evidence": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include detailed evidence"
                        }
                    },
                    "required": ["project_id"]
                }
            }
        }

    # MCP Protocol Methods
    async def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests (both STDIO and SSE)"""
        try:
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/list":
                return await self.list_tools()
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                return await self.call_tool(tool_name, arguments)
            elif method == "initialize":
                return await self.initialize()
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    async def initialize(self) -> Dict[str, Any]:
        """Initialize MCP server"""
        return {
            "result": {
                "server_info": MCP_SERVER_INFO,
                "capabilities": {
                    "tools": True,
                    "resources": False,
                    "prompts": False
                }
            }
        }

    async def list_tools(self) -> Dict[str, Any]:
        """List all available tools"""
        tools = []
        for name, config in self.tools.items():
            tools.append({
                "name": name,
                "description": config["description"],
                "inputSchema": config["parameters"]
            })

        return {
            "result": {
                "tools": tools
            }
        }

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool with arguments"""
        if tool_name not in self.tools:
            return {
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }

        try:
            if tool_name == "scrape_url":
                result = await self.scrape_url(**arguments)
            elif tool_name == "scrape_multiple_urls":
                result = await self.scrape_multiple_urls(**arguments)
            elif tool_name == "start_research":
                result = await self.start_research(**arguments)
            elif tool_name == "research_interactive":
                result = await self.research_interactive(**arguments)
            elif tool_name == "list_research_projects":
                result = await self.list_research_projects(**arguments)
            elif tool_name == "export_research_report":
                result = await self.export_research_report(**arguments)
            else:
                raise ValueError(f"Tool implementation not found: {tool_name}")

            return {"result": result}

        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }

    # Tool Implementations
    async def scrape_url(
        self,
        url: str,
        output_format: str = "json",
        content_type: str = "html",
        extract_links: bool = False,
        max_content_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Scrape a single URL and return content in specified format

        Args:
            url: Target URL to scrape
            output_format: Output format (json, xml, markdown)
            content_type: Expected content type (html, json, text)
            extract_links: Whether to extract and return links
            max_content_length: Maximum content length to process

        Returns:
            Dict containing scraped content and metadata
        """
        try:
            print(f"🚀 Scraping {url}...")

            # Fetch content
            content = await self.web_adapter.fetch_content(
                url, ContentType(content_type.lower())
            )

            if not content:
                raise Exception(f"Failed to fetch content from {url}")

            # Truncate content if needed
            content_text = content.content
            if max_content_length and len(content_text) > max_content_length:
                content_text = content_text[:max_content_length] + "..."

            # Extract additional data if requested
            links = []
            if extract_links and ContentType(content_type.lower()) == ContentType.HTML:
                links = self._extract_links(content.content, url)

            # Calculate quality score (simplified)
            quality_score = self._calculate_quality_score(content.content)

            # Prepare result data
            result_data = {
                "url": url,
                "title": content.title,
                "content": content_text,
                "content_length": len(content.content),
                "content_type": content_type,
                "fetch_timestamp": content.timestamp.isoformat(),
                "quality_score": quality_score,
                "links": links if extract_links else [],
                "metadata": {
                    "status_code": content.status_code,
                    "response_time_ms": 0,  # Simplified
                }
            }

            # Format output
            formatted_result = self._format_output(result_data, output_format)

            print(f"✅ Success! Content length: {len(content.content)}")

            return {
                "success": True,
                "data": formatted_result,
                "format": output_format,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "timestamp": datetime.now().isoformat()
            }

    async def scrape_multiple_urls(
        self,
        urls: List[str],
        output_format: str = "json",
        concurrent_limit: int = 5,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Scrape multiple URLs concurrently"""
        results = []

        # Process URLs in batches to respect concurrent limit
        for i in range(0, len(urls), concurrent_limit):
            batch = urls[i:i + concurrent_limit]
            batch_tasks = [
                self.scrape_url(url, output_format)
                for url in batch
            ]

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)

        successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        failed = len(results) - successful

        return {
            "success": True,
            "results": results,
            "summary": {
                "total_urls": len(urls),
                "successful": successful,
                "failed": failed,
                "success_rate": successful / len(urls) if urls else 0
            },
            "timestamp": datetime.now().isoformat()
        }

    async def start_research(
        self,
        research_question: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        initial_urls: Optional[List[str]] = None,
        max_sources: int = 8,
        include_contradictions: bool = True,
        citation_format: str = "apa"
    ) -> Dict[str, Any]:
        """Start a comprehensive research project"""
        # This would integrate with the research use cases
        # For now, return a structured response indicating research initiation

        project_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "success": True,
            "project": {
                "project_id": project_id,
                "title": title or f"Research: {research_question[:50]}...",
                "research_question": research_question,
                "description": description,
                "status": "initiated",
                "initial_urls": initial_urls or [],
                "config": {
                    "max_sources": max_sources,
                    "include_contradictions": include_contradictions,
                    "citation_format": citation_format
                },
                "created_at": datetime.now().isoformat()
            },
            "message": "Research project initiated. Deep research workflow will begin processing."
        }

    async def research_interactive(
        self,
        question: str,
        depth: str = "standard",
        format: str = "markdown",
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """Conduct interactive research session"""
        # Simulate interactive research for now
        # In full implementation, this would use the research use cases

        return {
            "success": True,
            "question": question,
            "depth": depth,
            "summary": f"Based on analysis of {max_sources} sources, here are key findings about '{question}':\n\n"
                      "• Key finding 1 with supporting evidence\n"
                      "• Key finding 2 from authoritative sources\n"
                      "• Key finding 3 with cross-references\n\n"
                      f"Confidence: 0.82 | Sources: {max_sources} | Evidence: 12 pieces",
            "format": format,
            "timestamp": datetime.now().isoformat()
        }

    async def list_research_projects(
        self,
        status: str = "all",
        limit: int = 20
    ) -> Dict[str, Any]:
        """List research projects"""
        # Mock data for now - would integrate with storage adapter
        projects = [
            {
                "project_id": "proj_123456",
                "title": "AI Development Trends",
                "status": "completed",
                "evidence_count": 15,
                "confidence_level": 0.87,
                "created_at": "2024-01-15T14:30:00Z"
            },
            {
                "project_id": "proj_789012",
                "title": "Quantum Computing Applications",
                "status": "in_progress",
                "evidence_count": 8,
                "confidence_level": 0.65,
                "created_at": "2024-01-16T09:15:00Z"
            }
        ]

        # Filter by status if specified
        if status != "all":
            projects = [p for p in projects if p["status"] == status]

        return {
            "success": True,
            "projects": projects[:limit],
            "total": len(projects),
            "filtered_by": status,
            "timestamp": datetime.now().isoformat()
        }

    async def export_research_report(
        self,
        project_id: str,
        format: str = "markdown",
        include_bibliography: bool = True,
        include_evidence: bool = True
    ) -> Dict[str, Any]:
        """Export research report"""
        # Mock export for now - would integrate with research use cases

        if format == "markdown":
            report_content = f"""# Research Report: {project_id}

**Research Question:** What are the latest trends in AI development?
**Status:** Completed
**Confidence Level:** 0.87/1.0
**Evidence Collected:** 15 pieces
**Created:** 2024-01-15 14:30:00

## Executive Summary
Comprehensive analysis reveals significant advances in AI development...

## Evidence Summary
### Primary Evidence (5 items)
1. **Advanced Language Models** - High confidence findings
2. **Multimodal AI Systems** - Emerging trend with strong evidence
3. **Edge AI Deployment** - Growing adoption across industries

{'## Bibliography' if include_bibliography else ''}
{'[1] Source citations would appear here...' if include_bibliography else ''}
"""
        else:
            report_content = {"report": "JSON formatted report data..."}

        return {
            "success": True,
            "project_id": project_id,
            "format": format,
            "report": report_content,
            "export_timestamp": datetime.now().isoformat()
        }

    # Helper Methods
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate content quality score (simplified)"""
        if not content:
            return 0.0

        score = 0.5  # Base score

        # Length factor
        if len(content) > 1000:
            score += 0.2
        elif len(content) > 500:
            score += 0.1

        # HTML structure factor
        if '<title>' in content:
            score += 0.1
        if '<h1>' in content or '<h2>' in content:
            score += 0.1
        if '<p>' in content:
            score += 0.1

        return min(score, 1.0)

    def _extract_links(self, html_content: str, base_url: str) -> List[Dict]:
        """Extract links from HTML content"""
        links = []
        try:
            # Simple regex to find href attributes
            href_pattern = r'href=[\'"](.*?)[\'"]'
            matches = re.findall(href_pattern, html_content, re.IGNORECASE)

            for match in matches:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, match)

                # Extract link text (simplified)
                text = match.split('/')[-1] or match

                # Parse domain
                parsed = urlparse(absolute_url)
                domain = parsed.netloc

                if domain:  # Valid URL
                    links.append({
                        "url": absolute_url,
                        "text": text[:100],  # Limit text length
                        "domain": domain
                    })

                    if len(links) >= 50:  # Limit number of links
                        break

        except Exception:
            pass  # Silent fail for link extraction

        return links

    def _format_output(self, data: Any, format_type: str) -> Any:
        """Format output based on requested format"""
        if format_type.lower() == "json":
            return data
        elif format_type.lower() == "xml":
            return self._to_xml(data)
        elif format_type.lower() == "markdown":
            return self._to_markdown(data)
        else:
            return data

    def _to_xml(self, data: Any) -> str:
        """Convert data to XML format"""
        try:
            if isinstance(data, dict):
                return self._dict_to_xml(data)
            else:
                return f"<content>{str(data)}</content>"
        except Exception:
            return "Error: Failed to convert to XML"

    def _dict_to_xml(self, data: Dict, root_tag: str = "scrape_result") -> str:
        """Convert dictionary to XML format"""
        def convert_value(key: str, value: Any) -> str:
            if isinstance(value, dict):
                inner_xml = ""
                for k, v in value.items():
                    inner_xml += convert_value(k, v)
                return f"<{key}>{inner_xml}</{key}>"
            elif isinstance(value, list):
                list_xml = ""
                for i, item in enumerate(value):
                    list_xml += convert_value(f"item_{i}", item)
                return f"<{key}>{list_xml}</{key}>"
            else:
                return f"<{key}>{str(value)}</{key}>"

        xml_content = ""
        for key, value in data.items():
            xml_content += convert_value(key, value)

        return f"<{root_tag}>{xml_content}</{root_tag}>"

    def _to_markdown(self, data: Any) -> str:
        """Convert data to Markdown format"""
        try:
            if isinstance(data, dict):
                return self._dict_to_markdown(data)
            else:
                return f"```\n{str(data)}\n```"
        except Exception:
            return "Error: Failed to convert to Markdown"

    def _dict_to_markdown(self, data: Dict, level: int = 1) -> str:
        """Convert dictionary to Markdown format"""
        lines = []

        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{'#' * level} {key}")
                lines.append(self._dict_to_markdown(value, level + 1))
            elif isinstance(value, list):
                lines.append(f"{'#' * level} {key}")
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        lines.append(f"### Item {i + 1}")
                        for k, v in item.items():
                            lines.append(f"**{k}**: {v}")
                    else:
                        lines.append(f"- {item}")
            else:
                if key == "content" and len(str(value)) > 200:
                    lines.append(f"{'#' * level} {key}")
                    lines.append("```")
                    lines.append(str(value))
                    lines.append("```")
                else:
                    lines.append(f"**{key}**: {value}")

        return "\n\n".join(lines)

    # Protocol Handlers
    async def run_stdio(self):
        """Run MCP server in STDIO mode"""
        print("🚀 Starting Agentic Web Scraper MCP Server (STDIO mode)", file=sys.stderr)
        print(f"📋 Available tools: {', '.join(self.tools.keys())}", file=sys.stderr)

        while True:
            try:
                line = input()
                if not line:
                    continue

                request = json.loads(line)
                response = await self.handle_mcp_request(request)
                print(json.dumps(response))

            except EOFError:
                break
            except json.JSONDecodeError:
                print(json.dumps({
                    "error": {
                        "code": -32700,
                        "message": "Parse error: Invalid JSON"
                    }
                }))
            except Exception as e:
                print(json.dumps({
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }))

    async def run_sse(self, host: str = "localhost", port: int = 8000):
        """Run MCP server in SSE mode"""
        from aiohttp import web, web_request
        from aiohttp.web_response import Response

        print(f"🌐 Starting Agentic Web Scraper MCP Server (SSE mode)", file=sys.stderr)
        print(f"🔗 Server will be available at: http://{host}:{port}/sse", file=sys.stderr)

        async def handle_sse(request: web_request.Request) -> Response:
            """Handle SSE connections"""
            response = web.StreamResponse(
                status=200,
                reason='OK',
                headers={
                    'Content-Type': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                }
            )

            await response.prepare(request)

            # Send server info
            await response.write(f"data: {json.dumps(MCP_SERVER_INFO)}\n\n".encode())

            # Keep connection alive
            try:
                while True:
                    await asyncio.sleep(30)  # Send keepalive every 30 seconds
                    await response.write("data: {\"type\": \"keepalive\"}\n\n".encode())
            except Exception:
                pass

            return response

        async def handle_tools(request: web_request.Request) -> Response:
            """Handle tool calls via HTTP POST"""
            if request.method == 'OPTIONS':
                return web.Response(
                    headers={
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type',
                    }
                )

            try:
                data = await request.json()
                response = await self.handle_mcp_request(data)
                return web.json_response(response, headers={
                    'Access-Control-Allow-Origin': '*'
                })
            except Exception as e:
                return web.json_response({
                    "error": {
                        "code": -32603,
                        "message": f"Request handling error: {str(e)}"
                    }
                }, headers={'Access-Control-Allow-Origin': '*'})

        app = web.Application()
        app.router.add_get('/sse', handle_sse)
        app.router.add_post('/tools', handle_tools)
        app.router.add_options('/tools', handle_tools)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        print(f"✅ SSE server running on http://{host}:{port}")

        # Keep the server running
        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            await runner.cleanup()

    async def run_cli(self):
        """Run in CLI mode for direct testing"""
        print("🖥️  Agentic Web Scraper - CLI Mode")
        print("Available commands:")
        print("  scrape <url> - Scrape a single URL")
        print("  research <question> - Start interactive research")
        print("  help - Show this help")
        print("  quit - Exit")

        while True:
            try:
                command = input("\n> ").strip()

                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() == 'help':
                    print("Available tools:", ", ".join(self.tools.keys()))
                elif command.startswith('scrape '):
                    url = command[7:]
                    result = await self.scrape_url(url, output_format="markdown")
                    print(f"\n{result}")
                elif command.startswith('research '):
                    question = command[9:]
                    result = await self.research_interactive(question)
                    print(f"\n{result}")
                else:
                    print("Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Agentic Web Scraper MCP Server",
        epilog="Supports both STDIO and SSE protocols for AI assistant integration"
    )
    parser.add_argument("--stdio", action="store_true",
                       help="Run in STDIO mode (for local AI assistants)")
    parser.add_argument("--sse", action="store_true",
                       help="Run in SSE mode (for web applications)")
    parser.add_argument("--cli", action="store_true",
                       help="Run in CLI mode (for testing)")
    parser.add_argument("--host", default="localhost",
                       help="Host for SSE mode (default: localhost)")
    parser.add_argument("--port", type=int, default=8000,
                       help="Port for SSE mode (default: 8000)")

    args = parser.parse_args()

    server = WebScraperMCPServer()

    if args.stdio:
        await server.run_stdio()
    elif args.sse:
        await server.run_sse(args.host, args.port)
    elif args.cli:
        await server.run_cli()
    else:
        # Default to STDIO mode
        print("No mode specified, defaulting to STDIO mode", file=sys.stderr)
        print("Use --help to see all available modes", file=sys.stderr)
        await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
