"""
기본 테스트
"""
import sys
sys.path.insert(0, 'src')

import pytest
from universal_http_api_client import HTTPAPIClient, Platform, __version__


def test_version():
    """버전 정보 테스트"""
    assert __version__ == "1.0.0"


def test_import():
    """기본 import 테스트"""
    from universal_http_api_client import (
        HTTPAPIClient,
        AsyncHTTPAPIClient,
        Platform,
        APIError,
        setup_logging
    )
    
    assert HTTPAPIClient is not None
    assert AsyncHTTPAPIClient is not None
    assert Platform is not None
    assert APIError is not None
    assert setup_logging is not None


def test_client_creation():
    """클라이언트 생성 테스트"""
    client = HTTPAPIClient(
        platform=Platform.GITHUB,
        auth_token="test_token"
    )
    
    assert client.platform == Platform.GITHUB
    assert client.auth_token == "test_token"
    
    client.close()


if __name__ == "__main__":
    pytest.main([__file__])
