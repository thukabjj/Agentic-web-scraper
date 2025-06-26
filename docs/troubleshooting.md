# 🔍 Troubleshooting Guide

## Common Issues & Solutions

### Installation Problems
- **UV Installation Fails**: Use sudo or fix permissions
- **Dependencies Installation Issues**: Create a fresh environment
- **Playwright Installation Fails**: Install system dependencies first

### Runtime Errors
- **API Key Issues**: Check environment variables and .env file
- **Connection Errors**: Adjust timeout and retry settings
- **Memory Issues**: Enable batch processing and monitor usage

### Dynamic Content Issues
- **Content Not Loading**: Add wait conditions or use Playwright
- **JavaScript Errors**: Handle JS errors gracefully

### Analysis Problems
- **Poor Analysis Quality**: Adjust analysis parameters and focus areas
- **Research Issues**: Expand research parameters and validate sources

## Debugging Tips
- Enable debug logging: `export LOG_LEVEL=debug`
- Check server status and metrics endpoints
- Monitor resource usage with built-in tools

## Recovery Procedures
- Backup and restore configuration
- Graceful shutdown and cleanup

## STDIO/CLI Output Separation

- As of the latest update, all logs and status messages (such as initialization, adapter loading, etc.) are printed to **stderr**.
- Only valid JSON responses are printed to **stdout** in STDIO mode.
- This ensures compatibility with AI assistants and automated tools, and all protocol tests now pass.

For more help, see the [Wiki](https://github.com/thukabjj/Agentic-web-scraper/wiki) or open an issue on GitHub.

For installation, see [Installation Guide](installation.md). For usage, see [Usage Guide](usage.md).
