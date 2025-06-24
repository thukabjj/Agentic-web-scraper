#!/usr/bin/env python3
"""
Tests for MCP SSE Protocol

Tests the Model Context Protocol SSE implementation for web-based integration
with comprehensive coverage of all tools and HTTP endpoints.
"""

import asyncio
import json
from typing import Any, Dict

import aiohttp
import pytest


class TestMCPSSE:
    """Test suite for MCP SSE protocol"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.server_process = None

    async def start_sse_server(self):
        """Start the MCP SSE server for testing"""
        self.server_process = await asyncio.create_subprocess_exec(
            "python", "mcp_server.py", "--sse", "--port", "8000",
            stderr=asyncio.subprocess.PIPE
        )
        # Give server time to start
        await asyncio.sleep(2)

    async def stop_sse_server(self):
        """Stop the MCP SSE server"""
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()

    async def send_tool_request(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a tool request to the SSE server"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tools",
                json=tool_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                return await response.json()

    async def test_sse_connection(self):
        """Test SSE connection establishment"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/sse") as response:
                assert response.status == 200
                assert response.headers.get("Content-Type") == "text/event-stream"

    @pytest.mark.asyncio
    async def test_sse_tools_endpoint(self):
        """Test tools endpoint via HTTP POST"""
        await self.start_sse_server()

        try:
            tool_request = {
                "method": "tools/list",
                "params": {}
            }

            response = await self.send_tool_request(tool_request)

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

        finally:
            await self.stop_sse_server()

    @pytest.mark.asyncio
    async def test_sse_scrape_url_tool(self):
        """Test scrape_url tool via SSE"""
        await self.start_sse_server()

        try:
            tool_request = {
                "method": "tools/call",
                "params": {
                    "name": "scrape_url",
                    "arguments": {
                        "url": "https://httpbin.org/html",
                        "output_format": "json"
                    }
                }
            }

            response = await self.send_tool_request(tool_request)

            assert "result" in response
            result = response["result"]

            assert result["success"] is True
            assert "data" in result
            assert "url" in result["data"]

        finally:
            await self.stop_sse_server()

    @pytest.mark.asyncio
    async def test_sse_research_tool(self):
        """Test research tool via SSE"""
        await self.start_sse_server()

        try:
            tool_request = {
                "method": "tools/call",
                "params": {
                    "name": "start_research",
                    "arguments": {
                        "research_question": "What is artificial intelligence?",
                        "title": "AI Research Test",
                        "max_sources": 3
                    }
                }
            }

            response = await self.send_tool_request(tool_request)

            assert "result" in response
            result = response["result"]

            assert result["success"] is True
            assert "project" in result
            assert "project_id" in result["project"]

        finally:
            await self.stop_sse_server()

    @pytest.mark.asyncio
    async def test_sse_cors_headers(self):
        """Test CORS headers in SSE responses"""
        await self.start_sse_server()

        try:
            async with aiohttp.ClientSession() as session:
                # Test OPTIONS request
                async with session.options(f"{self.base_url}/tools") as response:
                    assert response.status == 200
                    assert "Access-Control-Allow-Origin" in response.headers
                    assert response.headers["Access-Control-Allow-Origin"] == "*"

        finally:
            await self.stop_sse_server()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
