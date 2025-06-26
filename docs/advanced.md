# 🔧 Advanced Features & Configuration

## Advanced CLI & API Usage

- Use advanced flags in CLI: `--output-format`, `--content-type`, `--extract-links`, `--max-content-length`
- Batch processing, session management, and authentication
- Custom extraction rules and site-specific configuration

## Configuration Options

### Environment Variables
```bash
# Required API Keys
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here

# Optional: Custom Endpoints
OLLAMA_BASE_URL=http://localhost:11434/api
```

### Python Configuration Classes
```python
from config import AnalyzerConfig

config = AnalyzerConfig(
    timeout=30,
    rate_limit=10,
    retries=3,
    enable_caching=True,
    use_playwright=False,
    output_format='json',
    include_metadata=True
)
```

## Performance Optimization
- Set appropriate `rate_limit` and `timeout`
- Enable caching for frequently accessed content
- Use `max_concurrent` and `connection_pool_size` for scaling
- Monitor resource usage and optimize batch sizes

## Best Practices
- Always use a virtual environment
- Handle errors gracefully and log issues
- Respect robots.txt and site terms of service
- Keep API keys secure
- Regularly update dependencies

For troubleshooting, see [Troubleshooting](troubleshooting.md). For usage, see [Usage Guide](usage.md).
