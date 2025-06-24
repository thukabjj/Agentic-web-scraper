#!/usr/bin/env python3
"""
Tests for MCP STDIO Protocol

Tests the Model Context Protocol STDIO implementation with comprehensive
coverage of all tools and error handling scenarios.
"""

import asyncio
import json
import subprocess
import sys
from typing import Any, Dict

import pytest


class TestMCPSTDIO:
    """Test suite for MCP STDIO protocol"""

    async def send_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send an MCP request via STDIO and get response"""
        # Start the MCP server process
        process = await asyncio.create_subprocess_exec(
            sys.executable, "mcp_server.py", "--stdio",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Send request
        request_json = json.dumps(request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()

        # Read response
        response_line = await process.stdout.readline()
        process.terminate()
        await process.wait()

        if response_line:
            return json.loads(response_line.decode().strip())
        else:
            raise Exception("No response received from MCP server")

    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test MCP server initialization"""
        request = {
            "method": "initialize",
            "params": {}
        }

        response = await self.send_mcp_request(request)

        assert "result" in response
        assert "server_info" in response["result"]
        assert response["result"]["server_info"]["name"] == "agentic-web-scraper"
        assert "capabilities" in response["result"]
        assert response["result"]["capabilities"]["tools"] is True

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available MCP tools"""
        request = {
            "method": "tools/list",
            "params": {}
        }

        response = await self.send_mcp_request(request)

        assert "result" in response
        assert "tools" in response["result"]

        tools = response["result"]["tools"]
        tool_names = [tool["name"] for tool in tools]

        expected_tools = [
            "scrape_url",
            "scrape_multiple_urls",
            "start_research",
            "research_interactive",
            "list_research_projects",
            "export_research_report"
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_scrape_url_tool(self):
        """Test the scrape_url tool via STDIO"""
        request = {
            "method": "tools/call",
            "params": {
                "name": "scrape_url",
                "arguments": {
                    "url": "https://httpbin.org/html",
                    "output_format": "json"
                }
            }
        }

        response = await self.send_mcp_request(request)

        assert "result" in response
        result = response["result"]

        assert result["success"] is True
        assert "data" in result
        assert "url" in result["data"]
        assert result["data"]["url"] == "https://httpbin.org/html"

    @pytest.mark.asyncio
    async def test_scrape_multiple_urls_tool(self):
        """Test the scrape_multiple_urls tool via STDIO"""
        request = {
            "method": "tools/call",
            "params": {
                "name": "scrape_multiple_urls",
                "arguments": {
                    "urls": [
                        "https://httpbin.org/html",
                        "https://httpbin.org/json"
                    ],
                    "concurrent_limit": 2
                }
            }
        }

        response = await self.send_mcp_request(request)

        assert "result" in response
        result = response["result"]

        assert result["success"] is True
        assert "results" in result
        assert len(result["results"]) == 2
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_start_research_tool(self):
        """Test the start_research tool via STDIO"""
        request = {
            "method": "tools/call",
            "params": {
                "name": "start_research",
                "arguments": {
                    "research_question": "What are the benefits of renewable energy?",
                    "title": "Renewable Energy Research",
                    "max_sources": 5
                }
            }
        }

        response = await self.send_mcp_request(request)

        assert "result" in response
        result = response["result"]

        assert result["success"] is True
        assert "project" in result
        assert "project_id" in result["project"]
        assert result["project"]["status"] == "initiated"

    @pytest.mark.asyncio
    async def test_research_interactive_tool(self):
        """Test the research_interactive tool via STDIO"""
        request = {
            "method": "tools/call",
            "params": {
                "name": "research_interactive",
                "arguments": {
                    "question": "What is machine learning?",
                    "depth": "quick",
                    "max_sources": 3
                }
            }
        }

        response = await self.send_mcp_request(request)

        assert "result" in response
        result = response["result"]

        assert result["success"] is True
        assert "question" in result
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_list_research_projects_tool(self):
        """Test the list_research_projects tool via STDIO"""
        request = {
            "method": "tools/call",
            "params": {
                "name": "list_research_projects",
                "arguments": {
                    "status": "all",
                    "limit": 10
                }
            }
        }

        response = await self.send_mcp_request(request)

        assert "result" in response
        result = response["result"]

        assert result["success"] is True
        assert "projects" in result
        assert isinstance(result["projects"], list)

    @pytest.mark.asyncio
    async def test_export_research_report_tool(self):
        """Test the export_research_report tool via STDIO"""
        request = {
            "method": "tools/call",
            "params": {
                "name": "export_research_report",
                "arguments": {
                    "project_id": "proj_123456",
                    "format": "markdown",
                    "include_bibliography": True
                }
            }
        }

        response = await self.send_mcp_request(request)

        assert "result" in response
        result = response["result"]

        assert result["success"] is True
        assert "report" in result
        assert result["format"] == "markdown"

    @pytest.mark.asyncio
    async def test_unknown_tool_error(self):
        """Test error handling for unknown tools"""
        request = {
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {}
            }
        }

        response = await self.send_mcp_request(request)

        assert "error" in response
        assert response["error"]["code"] == -32602
        assert "Unknown tool" in response["error"]["message"]

    @pytest.mark.asyncio
    async def test_unknown_method_error(self):
        """Test error handling for unknown methods"""
        request = {
            "method": "unknown/method",
            "params": {}
        }

        response = await self.send_mcp_request(request)

        assert "error" in response
        assert response["error"]["code"] == -32601
        assert "Method not found" in response["error"]["message"]

    @pytest.mark.asyncio
    async def test_scrape_url_markdown_format(self):
        """Test scrape_url with markdown output format"""
        request = {
            "method": "tools/call",
            "params": {
                "name": "scrape_url",
                "arguments": {
                    "url": "https://httpbin.org/html",
                    "output_format": "markdown"
                }
            }
        }

        response = await self.send_mcp_request(request)

        assert "result" in response
        result = response["result"]

        assert result["success"] is True
        assert result["format"] == "markdown"
        assert isinstance(result["data"], str)

    @pytest.mark.asyncio
    async def test_scrape_url_xml_format(self):
        """Test scrape_url with XML output format"""
        request = {
            "method": "tools/call",
            "params": {
                "name": "scrape_url",
                "arguments": {
                    "url": "https://httpbin.org/html",
                    "output_format": "xml"
                }
            }
        }

        response = await self.send_mcp_request(request)

        assert "result" in response
        result = response["result"]

        assert result["success"] is True
        assert result["format"] == "xml"
        assert isinstance(result["data"], str)
        assert result["data"].startswith("<")

    @pytest.mark.asyncio
    async def test_scrape_url_with_links(self):
        """Test scrape_url with link extraction"""
        request = {
            "method": "tools/call",
            "params": {
                "name": "scrape_url",
                "arguments": {
                    "url": "https://httpbin.org/html",
                    "extract_links": True
                }
            }
        }

        response = await self.send_mcp_request(request)

        assert "result" in response
        result = response["result"]

        assert result["success"] is True
        assert "links" in result["data"]
        assert isinstance(result["data"]["links"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
