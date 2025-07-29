"""
Spyglasses exceptions and error types.
"""


class SpyglassesError(Exception):
    """Base exception for all Spyglasses errors."""
    
    pass


class ConfigurationError(SpyglassesError):
    """Raised when there's a configuration error."""
    
    pass


class ApiError(SpyglassesError):
    """Raised when there's an API error."""
    
    pass 