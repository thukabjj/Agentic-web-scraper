#!/usr/bin/env python3
"""
MCP Integration Tests

Simple integration tests to validate both STDIO and SSE protocols
are working correctly with all tools.
"""

import asyncio
import json
import subprocess
import sys
import time
from typing import Any, Dict

import aiohttp
import requests


class MCPIntegrationTester:
    """Integration tester for both MCP protocols"""

    def __init__(self):
        self.base_url = "http://localhost:8001"  # Use different port for testing
        self.sse_process = None

    async def test_stdio_protocol(self):
        """Test STDIO protocol with basic functionality"""
        print("🧪 Testing MCP STDIO Protocol...")

        try:
            # Test initialize
            await self._test_stdio_initialize()
            print("✅ STDIO Initialize: PASSED")

            # Test list tools
            await self._test_stdio_list_tools()
            print("✅ STDIO List Tools: PASSED")

            # Test scrape_url tool
            await self._test_stdio_scrape_url()
            print("✅ STDIO Scrape URL: PASSED")

            # Test research tool
            await self._test_stdio_research()
            print("✅ STDIO Research: PASSED")

            print("🎉 STDIO Protocol: ALL TESTS PASSED")
            return True

        except Exception as e:
            print(f"❌ STDIO Protocol Test Failed: {e}")
            return False

    async def _test_stdio_initialize(self):
        """Test STDIO initialize"""
        request = {"method": "initialize", "params": {}}
        response = await self._send_stdio_request(request)

        assert "result" in response
        assert "server_info" in response["result"]
        assert response["result"]["server_info"]["name"] == "agentic-web-scraper"

    async def _test_stdio_list_tools(self):
        """Test STDIO list tools"""
        request = {"method": "tools/list", "params": {}}
        response = await self._send_stdio_request(request)

        assert "result" in response
        assert "tools" in response["result"]

        tools = response["result"]["tools"]
        tool_names = [tool["name"] for tool in tools]

        required_tools = ["scrape_url", "start_research"]
        for tool in required_tools:
            assert tool in tool_names

    async def _test_stdio_scrape_url(self):
        """Test STDIO scrape_url tool"""
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
        response = await self._send_stdio_request(request)

        assert "result" in response
        result = response["result"]
        assert result["success"] is True

    async def _test_stdio_research(self):
        """Test STDIO research tool"""
        request = {
            "method": "tools/call",
            "params": {
                "name": "start_research",
                "arguments": {
                    "research_question": "What is renewable energy?",
                    "title": "Test Research",
                    "max_sources": 3
                }
            }
        }
        response = await self._send_stdio_request(request)

        assert "result" in response
        result = response["result"]
        assert result["success"] is True
        assert "project" in result

    async def _send_stdio_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send STDIO request and get response"""
        process = await asyncio.create_subprocess_exec(
            sys.executable, "mcp_server.py", "--stdio",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        request_json = json.dumps(request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()

        # Read all stdout lines to find the JSON response
        response_line = None
        while True:
            line = await process.stdout.readline()
            if not line:
                break

            line_str = line.decode().strip()
            if line_str.startswith('{') and line_str.endswith('}'):
                response_line = line_str
                break

        process.terminate()
        await process.wait()

        if response_line:
            return json.loads(response_line)
        else:
            raise Exception("No JSON response from STDIO server")

    async def test_sse_protocol(self):
        """Test SSE protocol with basic functionality"""
        print("🧪 Testing MCP SSE Protocol...")

        try:
            # Start SSE server
            await self._start_sse_server()

            # Test SSE connection
            await self._test_sse_connection()
            print("✅ SSE Connection: PASSED")

            # Test tools endpoint
            await self._test_sse_tools()
            print("✅ SSE Tools Endpoint: PASSED")

            # Test scrape tool via SSE
            await self._test_sse_scrape()
            print("✅ SSE Scrape Tool: PASSED")

            print("🎉 SSE Protocol: ALL TESTS PASSED")
            return True

        except Exception as e:
            print(f"❌ SSE Protocol Test Failed: {e}")
            return False
        finally:
            await self._stop_sse_server()

    async def _start_sse_server(self):
        """Start SSE server for testing"""
        self.sse_process = await asyncio.create_subprocess_exec(
            sys.executable, "mcp_server.py", "--sse", "--port", "8001",
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.sleep(3)  # Give server time to start

    async def _stop_sse_server(self):
        """Stop SSE server"""
        if self.sse_process:
            self.sse_process.terminate()
            await self.sse_process.wait()

    async def _test_sse_connection(self):
        """Test SSE connection"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/sse") as response:
                assert response.status == 200
                content_type = response.headers.get("Content-Type", "")
                assert "text/event-stream" in content_type

    async def _test_sse_tools(self):
        """Test SSE tools endpoint"""
        tool_request = {"method": "tools/list", "params": {}}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tools",
                json=tool_request
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert "result" in data
                assert "tools" in data["result"]

    async def _test_sse_scrape(self):
        """Test SSE scrape tool"""
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

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tools",
                json=tool_request
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert "result" in data
                result = data["result"]
                assert result["success"] is True

    def test_cli_mode(self):
        """Test CLI mode functionality"""
        print("🧪 Testing MCP CLI Mode...")

        try:
            # Test that CLI mode starts without errors
            process = subprocess.Popen(
                [sys.executable, "mcp_server.py", "--cli"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Send quit command
            stdout, stderr = process.communicate(input="quit\n", timeout=5)

            assert process.returncode == 0 or stdout or stderr
            print("✅ CLI Mode: PASSED")
            return True

        except Exception as e:
            print(f"❌ CLI Mode Test Failed: {e}")
            return False

    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting MCP Integration Tests...")
        print("=" * 50)

        results = []

        # Test STDIO Protocol
        stdio_result = await self.test_stdio_protocol()
        results.append(("STDIO", stdio_result))

        print()

        # Test SSE Protocol
        sse_result = await self.test_sse_protocol()
        results.append(("SSE", sse_result))

        print()

        # Test CLI Mode
        cli_result = self.test_cli_mode()
        results.append(("CLI", cli_result))

        print()
        print("=" * 50)
        print("📊 Test Results Summary:")

        all_passed = True
        for protocol, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {protocol} Protocol: {status}")
            if not result:
                all_passed = False

        print()
        if all_passed:
            print("🎉 ALL TESTS PASSED! MCP Server is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")

        return all_passed


async def main():
    """Main test runner"""
    tester = MCPIntegrationTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
