# Spyglasses Python SDK

AI SEO, AI Agent Detection, AI Model Blocking, and Analytics for Python web applications.

The Spyglasses Python SDK enables you to detect AI Agents, bots, crawlers, and referrers in your Python web applications. It provides comprehensive [AI SEO](https://www.spyglasses.io), shows you when your site features in ChatGPT, Claude, Perplexity, and other AI assistant chat platforms. It can also prevent your site's content from being used for training AI by blocking the crawlers that scrape your content for training. It integrates seamlessly with popular Python web frameworks including Django, Flask, and FastAPI.

## Features

- **AI Bot Detection**: Identify AI crawlers, model trainers, and assistants
- **AI Referrer Detection**: Track traffic from AI platforms like ChatGPT, Claude, Perplexity
- **Framework Integration**: Built-in middleware for Django, Flask, FastAPI, WSGI, and ASGI
- **Pattern Management**: Auto-sync detection patterns from Spyglasses API
- **Custom Rules**: Configure custom blocking and allowing rules
- **Request Logging**: Automatic logging to Spyglasses collector for analytics
- **Thread Safe**: Designed for multi-threaded web applications
- **Type Hints**: Full typing support for better development experience

## Installation

### Basic Installation

```bash
pip install spyglasses
```

### Framework-Specific Installation

```bash
# For Django projects
pip install 'spyglasses[django]'

# For Flask projects  
pip install 'spyglasses[flask]'

# For FastAPI projects
pip install 'spyglasses[fastapi]'

# For development (includes testing tools)
pip install 'spyglasses[dev]'
```

## Quick Start

### 1. Get Your API Key

Sign up at [spyglasses.io](https://spyglasses.io) and get your API key from the dashboard.

### 2. Set Environment Variables

```bash
export SPYGLASSES_API_KEY="your-api-key-here"
export SPYGLASSES_DEBUG="true"  # Optional: for debugging
```

### 3. Framework Integration

#### Django

Add to your `settings.py`:

```python
MIDDLEWARE = [
    'spyglasses.middleware.DjangoMiddleware',
    # ... your other middleware
]

# Optional: Configure Spyglasses settings
SPYGLASSES_API_KEY = os.getenv('SPYGLASSES_API_KEY')
SPYGLASSES_DEBUG = True
```

Or configure programmatically:

```python
# In your middleware configuration
from spyglasses.middleware import DjangoMiddleware

# Add to Django middleware
MIDDLEWARE = [
    DjangoMiddleware,
    # ... other middleware
]
```

#### Flask

```python
from flask import Flask
from spyglasses.middleware import FlaskMiddleware

app = Flask(__name__)

# Initialize middleware
middleware = FlaskMiddleware(
    app=app,
    api_key="your-api-key",
    debug=True
)

# Or use as decorator for specific routes
from spyglasses.middleware.flask import spyglasses_middleware

@app.route('/api/data')
@spyglasses_middleware(api_key="your-api-key")
def get_data():
    return {"data": "sensitive information"}
```

#### FastAPI

```python
from fastapi import FastAPI
from spyglasses.middleware.fastapi import setup_spyglasses

app = FastAPI()

# Setup middleware
setup_spyglasses(
    app,
    api_key="your-api-key",
    debug=True
)

# Alternative manual setup
from spyglasses.middleware import FastAPIMiddleware
app.add_middleware(
    FastAPIMiddleware,
    api_key="your-api-key",
    debug=True
)
```

#### WSGI Applications

```python
from spyglasses.middleware import WSGIMiddleware

def application(environ, start_response):
    # Your WSGI app
    pass

# Wrap with Spyglasses middleware
application = WSGIMiddleware(
    application,
    api_key="your-api-key",
    debug=True
)
```

#### ASGI Applications

```python
from spyglasses.middleware import ASGIMiddleware

async def application(scope, receive, send):
    # Your ASGI app
    pass

# Wrap with Spyglasses middleware
application = ASGIMiddleware(
    application,
    api_key="your-api-key",
    debug=True
)
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SPYGLASSES_API_KEY` | Your Spyglasses API key | Required |
| `SPYGLASSES_DEBUG` | Enable debug logging | `false` |
| `SPYGLASSES_AUTO_SYNC` | Auto-sync patterns on startup | `true` |
| `SPYGLASSES_COLLECT_ENDPOINT` | Custom collector endpoint | `https://www.spyglasses.io/api/collect` |
| `SPYGLASSES_PATTERNS_ENDPOINT` | Custom patterns endpoint | `https://www.spyglasses.io/api/patterns` |
| `SPYGLASSES_CACHE_TTL` | Pattern cache TTL in seconds | `86400` (24 hours) |
| `SPYGLASSES_PLATFORM_TYPE` | Platform identifier | `python` |

### Programmatic Configuration

```python
from spyglasses import Configuration, Client

# Create custom configuration
config = Configuration(
    api_key="your-api-key",
    debug=True,
    auto_sync=True,
    platform_type="my-app",
    exclude_paths=["/admin", "/internal"]
)

# Use with client
client = Client(config)

# Or configure globally
import spyglasses
spyglasses.configure(config)
```

## Direct Usage (Without Middleware)

```python
from spyglasses import Client

# Initialize client
client = Client()

# Detect bot
user_agent = "Mozilla/5.0 (compatible; ChatGPT-User/1.0; +https://openai.com/bot)"
result = client.detect(user_agent)

if result.is_bot:
    print(f"Bot detected: {result.info.company} - {result.info.type}")
    if result.should_block:
        print("This bot should be blocked")

# Detect AI referrer
referrer = "https://chat.openai.com/"
result = client.detect_ai_referrer(referrer)

if result.source_type == "ai_referrer":
    print(f"AI referrer detected: {result.info.name}")

# Combined detection
result = client.detect(user_agent, referrer)

# Log request manually
request_info = {
    "url": "https://example.com/api/data",
    "user_agent": user_agent,
    "ip_address": "192.168.1.1",
    "request_method": "GET",
    "request_path": "/api/data",
    "request_query": "",
    "referrer": referrer,
    "response_status": 200,
    "response_time_ms": 150,
    "headers": {"Host": "example.com"}
}

client.log_request(result, request_info)
```

## Advanced Usage

### Custom Exclusions

```python
from spyglasses.middleware import DjangoMiddleware

# Exclude additional paths and file extensions
middleware = DjangoMiddleware(
    exclude_paths=["/health", "/metrics", "/admin"],
    exclude_extensions=[".ico", ".png", ".css"]
)
```

### Pattern Synchronization

```python
from spyglasses import Client

client = Client()

# Manual pattern sync
result = client.sync_patterns()
if isinstance(result, str):
    print(f"Sync failed: {result}")
else:
    print(f"Synced {len(result.patterns)} patterns")

# Check sync status
print(f"Last sync: {client.last_pattern_sync}")
print(f"Pattern version: {client.pattern_version}")
```

### Middleware Options

All middleware classes support these options:

```python
middleware = FrameworkMiddleware(
    api_key="your-api-key",
    debug=True,
    collect_endpoint="https://custom.endpoint.com/collect",
    patterns_endpoint="https://custom.endpoint.com/patterns", 
    auto_sync=True,
    platform_type="my-platform",
    cache_ttl=3600,  # 1 hour
    exclude_paths=["/admin", "/internal"],
    exclude_extensions=[".ico", ".png"]
)
```

## Bot Categories

Spyglasses detects various types of bots:

### AI Assistants
- ChatGPT-User (OpenAI user queries)
- Claude-User (Anthropic user queries)  
- Perplexity-User (Perplexity user queries)
- Gemini-User (Google user queries)

### AI Model Training Crawlers
- GPTBot (OpenAI training crawler)
- ClaudeBot (Anthropic training crawler)
- CCBot (Common Crawl)
- meta-externalagent (Meta training crawler)
- Applebot-Extended (Apple training crawler)

### AI Referrers
- Traffic from ChatGPT, Claude, Perplexity, Gemini, Microsoft Copilot

## Error Handling

The SDK is designed to be non-intrusive. If there are issues with the Spyglasses service:

- Pattern sync failures fall back to default patterns
- Network errors don't block requests
- Invalid configurations log warnings but don't crash
- All operations are wrapped in try/catch blocks

## Development

### Setting up Development Environment

```bash
git clone https://github.com/orchestra-code/spyglasses-python.git
cd spyglasses-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy src/

# Format code
black src/ tests/
ruff src/ tests/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=spyglasses

# Run specific test file
pytest tests/test_client.py

# Run integration tests
pytest -m integration
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Support

- Documentation: [spyglasses.io/docs](https://spyglasses.io/docs)
- Issues: [GitHub Issues](https://github.com/orchestra-code/spyglasses-python/issues)
- Support: [support@spyglasses.io](mailto:support@spyglasses.io)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
