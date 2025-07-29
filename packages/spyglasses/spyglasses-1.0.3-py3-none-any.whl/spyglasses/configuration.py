"""
Configuration management for Spyglasses.
"""

import os
from typing import List, Optional, Union
from urllib.parse import urlparse

from .exceptions import ConfigurationError


class Configuration:
    """Configuration for Spyglasses client."""
    
    DEFAULT_COLLECT_ENDPOINT = "https://www.spyglasses.io/api/collect"
    DEFAULT_PATTERNS_ENDPOINT = "https://www.spyglasses.io/api/patterns"
    DEFAULT_CACHE_TTL = 24 * 60 * 60  # 24 hours in seconds
    DEFAULT_PLATFORM_TYPE = "python"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        debug: Optional[bool] = None,
        collect_endpoint: Optional[str] = None,
        patterns_endpoint: Optional[str] = None,
        auto_sync: Optional[bool] = None,
        platform_type: Optional[str] = None,
        cache_ttl: Optional[int] = None,
        exclude_paths: Optional[List[Union[str, object]]] = None,
    ) -> None:
        """
        Initialize configuration.
        
        Args:
            api_key: Spyglasses API key
            debug: Enable debug logging
            collect_endpoint: Custom collector endpoint
            patterns_endpoint: Custom patterns endpoint
            auto_sync: Auto-sync patterns on startup
            platform_type: Platform identifier
            cache_ttl: Pattern cache TTL in seconds
            exclude_paths: Paths to exclude from monitoring
        """
        # Load from environment variables by default
        self.api_key = api_key or os.getenv("SPYGLASSES_API_KEY")
        self.debug = debug if debug is not None else os.getenv("SPYGLASSES_DEBUG", "").lower() == "true"
        self.collect_endpoint = collect_endpoint or os.getenv("SPYGLASSES_COLLECT_ENDPOINT", self.DEFAULT_COLLECT_ENDPOINT)
        self.patterns_endpoint = patterns_endpoint or os.getenv("SPYGLASSES_PATTERNS_ENDPOINT", self.DEFAULT_PATTERNS_ENDPOINT)
        self.auto_sync = auto_sync if auto_sync is not None else os.getenv("SPYGLASSES_AUTO_SYNC", "true").lower() != "false"
        self.platform_type = platform_type or os.getenv("SPYGLASSES_PLATFORM_TYPE", self.DEFAULT_PLATFORM_TYPE)
        
        # Handle cache_ttl conversion
        cache_ttl_env = os.getenv("SPYGLASSES_CACHE_TTL")
        if cache_ttl is not None:
            self.cache_ttl = cache_ttl
        elif cache_ttl_env:
            try:
                self.cache_ttl = int(cache_ttl_env)
            except ValueError:
                self.cache_ttl = self.DEFAULT_CACHE_TTL
        else:
            self.cache_ttl = self.DEFAULT_CACHE_TTL
            
        self.exclude_paths = exclude_paths or []
    
    def api_key_present(self) -> bool:
        """Check if API key is present and not empty."""
        return bool(self.api_key and self.api_key.strip())
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.debug
    
    def is_auto_sync(self) -> bool:
        """Check if auto-sync is enabled."""
        return self.auto_sync
    
    def validate(self) -> None:
        """
        Validate configuration.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not self.api_key_present():
            raise ConfigurationError(
                "API key is required. Set SPYGLASSES_API_KEY environment variable "
                "or provide api_key parameter"
            )
        
        if not self._is_valid_url(self.collect_endpoint):
            raise ConfigurationError(f"Invalid collect endpoint: {self.collect_endpoint}")
        
        if not self._is_valid_url(self.patterns_endpoint):
            raise ConfigurationError(f"Invalid patterns endpoint: {self.patterns_endpoint}")
        
        if self.cache_ttl < 0:
            raise ConfigurationError(f"Cache TTL must be non-negative: {self.cache_ttl}")
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation with masked API key
        """
        api_key_display = None
        if self.api_key:
            if len(self.api_key) > 8:
                api_key_display = f"{self.api_key[:8]}..."
            else:
                api_key_display = "***"
        
        return {
            "api_key": api_key_display,
            "debug": self.debug,
            "collect_endpoint": self.collect_endpoint,
            "patterns_endpoint": self.patterns_endpoint,
            "auto_sync": self.auto_sync,
            "platform_type": self.platform_type,
            "cache_ttl": self.cache_ttl,
            "exclude_paths": len(self.exclude_paths),
        }
    
    def _is_valid_url(self, url: Optional[str]) -> bool:
        """Check if URL is valid."""
        if not url:
            return False
        
        try:
            result = urlparse(url)
            return bool(result.scheme and result.netloc and result.scheme in ("http", "https"))
        except Exception:
            return False 