"""
Basic tests for Spyglasses package structure and imports.
"""

import pytest


def test_package_imports():
    """Test that main package components can be imported."""
    from spyglasses import Client, Configuration, __version__
    from spyglasses.exceptions import SpyglassesError, ConfigurationError, ApiError
    from spyglasses.types import DetectionResult, BotPattern, AiReferrerInfo
    
    assert __version__ == "1.0.0"
    assert Client is not None
    assert Configuration is not None


def test_basic_client_creation():
    """Test basic client creation and configuration."""
    from spyglasses import Client, Configuration
    
    # Test with default configuration
    client = Client()
    assert client is not None
    assert client.configuration is not None
    
    # Test with custom configuration
    config = Configuration(debug=True, auto_sync=False)
    client = Client(config)
    assert client.configuration.debug is True
    assert client.configuration.auto_sync is False


def test_detection_result_structure():
    """Test DetectionResult structure."""
    from spyglasses.types import DetectionResult, BotInfo
    
    # Test empty result
    result = DetectionResult()
    assert result.is_bot is False
    assert result.should_block is False
    assert result.source_type == "none"
    
    # Test bot result
    bot_info = BotInfo(
        pattern="TestBot/1.0",
        type="test-bot",
        category="Test",
        company="Test Corp"
    )
    
    result = DetectionResult(
        is_bot=True,
        should_block=True,
        source_type="bot",
        matched_pattern="TestBot/1.0",
        info=bot_info
    )
    
    assert result.is_bot is True
    assert result.should_block is True
    assert result.source_type == "bot"
    assert result.info.company == "Test Corp"


def test_collector_payload_format():
    """Test that CollectorPayload formats data correctly for API."""
    from spyglasses.types import CollectorPayload
    
    payload = CollectorPayload(
        url="https://example.com/test",
        user_agent="TestBot/1.0",
        ip_address="192.168.1.1",
        request_method="GET",
        request_path="/test",
        request_query="",
        response_status=200,
        response_time_ms=100,
        platform_type="python"
    )
    
    data = payload.to_dict()
    
    # Check required fields
    assert data["url"] == "https://example.com/test"
    assert data["user_agent"] == "TestBot/1.0"
    assert data["ip_address"] == "192.168.1.1"
    assert data["request_method"] == "GET"
    assert data["request_path"] == "/test"
    assert data["request_query"] == ""
    assert data["response_status"] == 200
    assert data["response_time_ms"] == 100
    
    # Check camelCase conversion
    assert "platformType" in data
    assert data["platformType"] == "python"
    assert "platform_type" not in data
    
    # Check timestamp is set
    assert "timestamp" in data
    assert data["timestamp"] is not None


def test_configuration_validation():
    """Test configuration validation."""
    from spyglasses import Configuration
    from spyglasses.exceptions import ConfigurationError
    
    # Test valid configuration
    config = Configuration(api_key="test-key")
    config.validate()  # Should not raise
    
    # Test missing API key
    config = Configuration()
    with pytest.raises(ConfigurationError, match="API key is required"):
        config.validate()
    
    # Test invalid endpoint
    config = Configuration(api_key="test-key", collect_endpoint="invalid-url")
    with pytest.raises(ConfigurationError, match="Invalid collect endpoint"):
        config.validate()


def test_middleware_imports():
    """Test that middleware components can be imported."""
    from spyglasses.middleware import BaseMiddleware, RequestInfo
    
    # Test optional imports (may not be available without framework dependencies)
    try:
        from spyglasses.middleware import WSGIMiddleware
        assert WSGIMiddleware is not None
    except ImportError:
        pass  # OK if WSGI dependencies not installed
    
    # These should always be available
    assert BaseMiddleware is not None
    assert RequestInfo is not None


if __name__ == "__main__":
    pytest.main([__file__]) 