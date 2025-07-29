"""
Spyglasses Python SDK

AI Agent Detection and Management for Python web applications.
"""

from typing import TYPE_CHECKING

__version__ = "1.0.3"

# Main components
from .client import Client
from .configuration import Configuration
from .exceptions import SpyglassesError, ConfigurationError, ApiError

# Type exports for convenience
if TYPE_CHECKING:
    from .types import (
        DetectionResult,
        BotPattern,
        BotInfo,
        AiReferrerInfo,
        ApiPatternResponse,
        PropertySettings,
        CollectorPayload,
    )

# Global configuration instance
_configuration: Configuration | None = None


def configure(config: Configuration | None = None) -> Configuration:
    """
    Configure Spyglasses globally.
    
    Args:
        config: Configuration instance or None to create default
        
    Returns:
        Configuration instance
    """
    global _configuration
    if config is not None:
        _configuration = config
    elif _configuration is None:
        _configuration = Configuration()
    return _configuration


def get_configuration() -> Configuration:
    """Get the global configuration, creating one if needed."""
    if _configuration is None:
        return configure()
    return _configuration


def reset_configuration() -> None:
    """Reset the global configuration."""
    global _configuration
    _configuration = None


__all__ = [
    "__version__",
    "Client",
    "Configuration",
    "SpyglassesError",
    "ConfigurationError", 
    "ApiError",
    "configure",
    "get_configuration",
    "reset_configuration",
] 