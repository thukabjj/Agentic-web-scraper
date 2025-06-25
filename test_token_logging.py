#!/usr/bin/env python3
"""
Test script for token logging functionality

This script demonstrates how to use the token logging system
to track LLM usage, costs, and performance metrics.
"""

import asyncio

from adapters.logging.token_logger import get_token_logger, log_llm_usage


async def test_token_logging():
    """Test the token logging functionality"""
    print("🧪 Testing Token Logging System...")
    print("=" * 50)

    # Get the token logger
    logger = get_token_logger()

    # Simulate some LLM operations
    test_operations = [
        {
            "provider": "ollama",
            "model": "qwen2.5:7b",
            "operation": "scrape_url",
            "input_tokens": 150,
            "output_tokens": 300,
            "duration": 2.5
        },
        {
            "provider": "perplexity",
            "model": "sonar-pro",
            "operation": "research",
            "input_tokens": 800,
            "output_tokens": 1200,
            "duration": 4.2
        },
        {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "operation": "analyze_url",
            "input_tokens": 500,
            "output_tokens": 750,
            "duration": 3.1
        },
        {
            "provider": "openai",
            "model": "gpt-4",
            "operation": "research_interactive",
            "input_tokens": 600,
            "output_tokens": 900,
            "duration": 2.8
        }
    ]

    session_id = "test_session_001"

    print("📊 Logging test operations...")
    for i, op in enumerate(test_operations, 1):
        print(f"  {i}. {op['operation']} with {op['provider']}/{op['model']}")

        # Log the usage
        usage = log_llm_usage(
            provider=op["provider"],
            model=op["model"],
            operation=op["operation"],
            input_tokens=op["input_tokens"],
            output_tokens=op["output_tokens"],
            duration_seconds=op["duration"],
            session_id=session_id,
            user_id="test_user"
        )

        print(f"     ✅ Logged: {usage.total_tokens} tokens, "
              f"{usage.tokens_per_second:.1f} tok/s, ${usage.cost_usd:.4f}")

        # Small delay to simulate real operations
        await asyncio.sleep(0.1)

    print("\n📈 Generating Reports...")
    print("-" * 30)

    # Get global metrics
    global_metrics = logger.get_global_metrics()
    print(f"🌍 Global Metrics:")
    print(f"   Total Requests: {global_metrics.total_requests}")
    print(f"   Total Tokens: {global_metrics.total_tokens:,}")
    print(f"   Input Tokens: {global_metrics.total_input_tokens:,}")
    print(f"   Output Tokens: {global_metrics.total_output_tokens:,}")
    print(f"   Total Cost: ${global_metrics.total_cost_usd:.4f}")
    print(f"   Avg Tokens/sec: {global_metrics.average_tokens_per_second:.1f}")

    # Get session metrics
    session_metrics = logger.get_session_metrics(session_id)
    if session_metrics:
        print(f"\n🎯 Session '{session_id}' Metrics:")
        print(f"   Total Requests: {session_metrics.total_requests}")
        print(f"   Total Tokens: {session_metrics.total_tokens:,}")
        print(f"   Total Cost: ${session_metrics.total_cost_usd:.4f}")
        print(f"   Avg Tokens/sec: {session_metrics.average_tokens_per_second:.1f}")

    # Generate detailed report
    print("\n📋 Detailed Report:")
    report = logger.generate_report(session_id)

    if "provider_breakdown" in report:
        print("   Provider Breakdown:")
        for provider, metrics in report["provider_breakdown"].items():
            print(f"     {provider}: {metrics['total_requests']} requests, "
                  f"${metrics['total_cost_usd']:.4f}")

    if "operation_breakdown" in report:
        print("   Operation Breakdown:")
        for operation, metrics in report["operation_breakdown"].items():
            print(f"     {operation}: {metrics['total_tokens']:,} tokens, "
                  f"{metrics['average_tokens_per_second']:.1f} tok/s")

    # Get recent usage
    print(f"\n📝 Recent Usage (last 5 records):")
    recent_usage = logger.get_recent_usage(5)
    for usage in recent_usage:
        print(f"   {usage.operation} | {usage.provider}/{usage.model} | "
              f"{usage.total_tokens} tokens | ${usage.cost_usd:.4f}")

    print("\n✅ Token logging test completed!")
    print(f"📁 Log files saved to: {logger.storage_path}")
    print(f"   - Usage log: {logger.log_file}")
    print(f"   - Metrics: {logger.metrics_file}")


async def test_mcp_integration():
    """Test token logging integration with MCP server"""
    print("\n🔌 Testing MCP Integration...")
    print("=" * 50)

    from mcp_server import WebScraperMCPServer

    # Initialize MCP server (which includes token logger)
    server = WebScraperMCPServer()

    # Test the get_token_metrics tool
    print("📊 Testing get_token_metrics tool...")

    # Test summary report
    result = await server.get_token_metrics(report_type="summary")
    print(f"✅ Summary report: {result['success']}")
    if result['success']:
        metrics = result['metrics']
        print(f"   Total requests: {metrics['total_requests']}")
        print(f"   Total tokens: {metrics['total_tokens']:,}")
        print(f"   Total cost: ${metrics['total_cost_usd']:.4f}")

    # Test recent report
    result = await server.get_token_metrics(report_type="recent", limit=3)
    print(f"✅ Recent report: {result['success']}")
    if result['success']:
        print(f"   Recent records: {result['count']}")

    # Test detailed report
    result = await server.get_token_metrics(report_type="detailed")
    print(f"✅ Detailed report: {result['success']}")

    print("✅ MCP integration test completed!")


if __name__ == "__main__":
    asyncio.run(test_token_logging())
    asyncio.run(test_mcp_integration())
