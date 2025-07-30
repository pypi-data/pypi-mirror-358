"""
Universal HTTP API Client - 범용 HTTP API 클라이언트

이 모듈은 GitHub, GitLab 등 다양한 플랫폼의 API를 호출하는 범용 클라이언트입니다.
재사용성을 고려하여 설계되었으며, 인증, 재시도, 캐싱 등의 기능을 제공합니다.
"""

__version__ = "1.0.0"

from .client import HTTPAPIClient, AsyncHTTPAPIClient
from .adapters import PlatformAPIAdapter, GitHubAdapter, GitLabAdapter
from .models import APIRequest, APIResponse, PlatformConfig, Platform, HTTPMethod
from .exceptions import APIError, RateLimitError, AuthenticationError, NetworkError, TimeoutError
from .utils import ModuleIOLogger, setup_logging

__all__ = [
    "HTTPAPIClient",
    "AsyncHTTPAPIClient",
    "PlatformAPIAdapter",
    "GitHubAdapter", 
    "GitLabAdapter",
    "APIRequest",
    "APIResponse",
    "PlatformConfig",
    "Platform",
    "HTTPMethod",
    "APIError",
    "RateLimitError",
    "AuthenticationError",
    "NetworkError",
    "TimeoutError",
    "ModuleIOLogger",
    "setup_logging",
    "__version__",
]
