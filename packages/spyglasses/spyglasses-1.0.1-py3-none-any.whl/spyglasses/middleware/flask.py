"""
Flask middleware for Spyglasses.
"""

import time
from functools import wraps
from typing import Any, Dict, List, Optional, Union

try:
    from flask import Flask, request, g, make_response, abort
    from werkzeug.exceptions import Forbidden
except ImportError:
    raise ImportError(
        "Flask is required to use FlaskMiddleware. "
        "Install it with: pip install 'spyglasses[flask]'"
    )

from ..configuration import Configuration
from .base import BaseMiddleware, RequestInfo


class FlaskMiddleware(BaseMiddleware):
    """Flask middleware for Spyglasses bot detection."""
    
    def __init__(
        self,
        app: Optional[Flask] = None,
        api_key: Optional[str] = None,
        debug: Optional[bool] = None,
        collect_endpoint: Optional[str] = None,
        patterns_endpoint: Optional[str] = None,
        auto_sync: Optional[bool] = None,
        platform_type: Optional[str] = None,
        cache_ttl: Optional[int] = None,
        exclude_paths: Optional[List[Union[str, object]]] = None,
        exclude_extensions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize Flask middleware.
        
        Args:
            app: Flask application instance
            api_key: Spyglasses API key
            debug: Enable debug logging
            collect_endpoint: Custom collector endpoint
            patterns_endpoint: Custom patterns endpoint
            auto_sync: Auto-sync patterns on startup
            platform_type: Platform identifier
            cache_ttl: Pattern cache TTL in seconds
            exclude_paths: Paths to exclude from monitoring
            exclude_extensions: File extensions to exclude
        """
        # Create configuration from parameters
        configuration = Configuration(
            api_key=api_key,
            debug=debug,
            collect_endpoint=collect_endpoint,
            patterns_endpoint=patterns_endpoint,
            auto_sync=auto_sync,
            platform_type=platform_type or "flask",
            cache_ttl=cache_ttl,
        )
        
        # Initialize base middleware
        super().__init__(
            configuration=configuration,
            exclude_paths=exclude_paths,
            exclude_extensions=exclude_extensions,
        )
        
        # Initialize with app if provided
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """
        Initialize middleware with Flask app.
        
        Args:
            app: Flask application instance
        """
        # Register before/after request handlers
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        # Store reference for potential cleanup
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['spyglasses'] = self
    
    def _before_request(self) -> Optional[Any]:
        """Before request handler."""
        # Store start time
        g.spyglasses_start_time = time.time()
        
        # Extract request information
        request_info = self._extract_request_info()
        
        # Process with base middleware
        detection_result = super().process_request(request_info)
        
        # Store detection result for after_request
        g.spyglasses_detection = detection_result
        g.spyglasses_request_info = request_info
        
        # Block if necessary
        if self.should_block_request(detection_result):
            status_code, headers, body = self.create_blocked_response()
            response = make_response(body, status_code)
            for key, value in headers.items():
                response.headers[key] = value
            return response
        
        return None
    
    def _after_request(self, response: Any) -> Any:
        """After request handler."""
        # Get stored data
        detection_result = getattr(g, 'spyglasses_detection', None)
        request_info = getattr(g, 'spyglasses_request_info', None)
        start_time = getattr(g, 'spyglasses_start_time', None)
        
        if detection_result and request_info and detection_result.source_type != "none":
            # Calculate response time
            response_time_ms = 0
            if start_time:
                response_time_ms = int((time.time() - start_time) * 1000)
            
            # Update request info with response data
            request_info.response_status = response.status_code
            request_info.response_time_ms = response_time_ms
            
            # Convert to dict and log
            request_dict = {
                "url": request_info.url,
                "user_agent": request_info.user_agent,
                "ip_address": request_info.ip_address,
                "request_method": request_info.request_method,
                "request_path": request_info.request_path,
                "request_query": request_info.request_query,
                "referrer": request_info.referrer,
                "response_status": request_info.response_status,
                "response_time_ms": request_info.response_time_ms,
                "headers": request_info.headers or {},
            }
            
            self.client.log_request(detection_result, request_dict)
        
        return response
    
    def _extract_request_info(self) -> RequestInfo:
        """
        Extract request information from Flask request.
        
        Returns:
            RequestInfo object
        """
        # Get headers as dict
        headers = dict(request.headers)
        
        # Extract IP address
        ip_address = self.extract_ip_address(
            headers,
            request.environ.get("REMOTE_ADDR", "")
        )
        
        # Build full URL
        scheme = request.scheme
        host = request.host
        path = request.path
        query = request.query_string.decode('utf-8')
        
        url = self.build_full_url(scheme, host, path, query)
        
        return RequestInfo(
            url=url,
            user_agent=request.headers.get("User-Agent", ""),
            ip_address=ip_address,
            request_method=request.method,
            request_path=path,
            request_query=query,
            referrer=request.headers.get("Referer"),
            headers=headers,
        )


def spyglasses_middleware(**kwargs) -> Any:
    """
    Decorator to add Spyglasses protection to Flask routes.
    
    Args:
        **kwargs: Configuration parameters for middleware
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **func_kwargs):
            # Create temporary middleware instance for this request
            middleware = FlaskMiddleware(**kwargs)
            
            # Check request
            request_info = middleware._extract_request_info()
            detection_result = middleware.process_request(request_info)
            
            if middleware.should_block_request(detection_result):
                status_code, headers, body = middleware.create_blocked_response()
                response = make_response(body, status_code)
                for key, value in headers.items():
                    response.headers[key] = value
                return response
            
            # Continue with original function
            return f(*args, **func_kwargs)
            
        return decorated_function
    return decorator 