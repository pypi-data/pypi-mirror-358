# Universal HTTP API Client

Universal HTTP API client with platform-specific adapters for GitHub, GitLab, Slack, and Notion.

## Features

- **Multi-Platform Support**: GitHub, GitLab, Slack, Notion APIs
- **Smart Caching**: Automatic request caching with configurable TTL
- **Rate Limiting**: Built-in rate limiting with platform-specific rules
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Async Support**: Full async/await support for all operations
- **Type Safety**: Complete type annotations with mypy support

## Installation

```bash
pip install universal-http-api-client
```

## Quick Start

```python
from universal_http_api_client import HTTPAPIClient, Platform

# GitHub API
client = HTTPAPIClient(Platform.GITHUB, "your-token")
repo = client.get_repository("owner/repo")
client.close()

# Slack API
slack_client = HTTPAPIClient(Platform.SLACK, "your-slack-token")
response = slack_client.send_message("channel", "Hello World!")
slack_client.close()
```

## License

MIT License
