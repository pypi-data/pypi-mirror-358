"""
WSGI middleware for Spyglasses.
"""

import time
from io import StringIO
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import parse_qs

from ..configuration import Configuration
from .base import BaseMiddleware, RequestInfo


class WSGIMiddleware(BaseMiddleware):
    """WSGI middleware for Spyglasses bot detection."""
    
    def __init__(
        self,
        app: Callable,
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
        Initialize WSGI middleware.
        
        Args:
            app: WSGI application callable
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
        self.app = app
        
        # Create configuration from parameters
        configuration = Configuration(
            api_key=api_key,
            debug=debug,
            collect_endpoint=collect_endpoint,
            patterns_endpoint=patterns_endpoint,
            auto_sync=auto_sync,
            platform_type=platform_type or "wsgi",
            cache_ttl=cache_ttl,
        )
        
        # Initialize base middleware
        super().__init__(
            configuration=configuration,
            exclude_paths=exclude_paths,
            exclude_extensions=exclude_extensions,
        )
    
    def __call__(self, environ: Dict[str, Any], start_response: Callable) -> Any:
        """
        WSGI application interface.
        
        Args:
            environ: WSGI environment dict
            start_response: WSGI start_response callable
            
        Returns:
            Response iterator
        """
        # Store start time
        start_time = time.time()
        
        # Extract request information
        request_info = self._extract_request_info(environ)
        
        # Process with base middleware
        detection_result = super().process_request(request_info)
        
        # Block if necessary
        if self.should_block_request(detection_result):
            status_code, headers, body = self.create_blocked_response()
            status_line = f"{status_code} Forbidden"
            response_headers = [(key, value) for key, value in headers.items()]
            start_response(status_line, response_headers)
            return [body.encode('utf-8')]
        
        # Capture response for logging
        captured_response = {"status": None, "headers": []}
        
        def capture_start_response(status: str, headers: List[tuple], exc_info: Any = None):
            captured_response["status"] = status
            captured_response["headers"] = headers
            return start_response(status, headers, exc_info)
        
        # Call original app
        response = self.app(environ, capture_start_response)
        
        # Log if needed
        if detection_result and detection_result.source_type != "none":
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Extract status code
            status_line = captured_response.get("status", "200 OK")
            status_code = int(status_line.split()[0]) if status_line else 200
            
            # Update request info with response data
            request_info.response_status = status_code
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
    
    def _extract_request_info(self, environ: Dict[str, Any]) -> RequestInfo:
        """
        Extract request information from WSGI environ.
        
        Args:
            environ: WSGI environment dict
            
        Returns:
            RequestInfo object
        """
        # Extract headers from environ
        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                # Convert HTTP_USER_AGENT to User-Agent
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value
            elif key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                # Special case for these headers
                headers[key.replace('_', '-').title()] = value
        
        # Extract IP address
        ip_address = self.extract_ip_address(
            headers,
            environ.get("REMOTE_ADDR", "")
        )
        
        # Build full URL
        scheme = environ.get('wsgi.url_scheme', 'http')
        server_name = environ.get('SERVER_NAME', 'localhost')
        server_port = environ.get('SERVER_PORT', '80')
        
        # Build host
        if (scheme == 'https' and server_port == '443') or (scheme == 'http' and server_port == '80'):
            host = server_name
        else:
            host = f"{server_name}:{server_port}"
        
        path = environ.get('PATH_INFO', '/')
        query = environ.get('QUERY_STRING', '')
        
        url = self.build_full_url(scheme, host, path, query)
        
        return RequestInfo(
            url=url,
            user_agent=environ.get('HTTP_USER_AGENT', ''),
            ip_address=ip_address,
            request_method=environ.get('REQUEST_METHOD', 'GET'),
            request_path=path,
            request_query=query,
            referrer=environ.get('HTTP_REFERER'),
            headers=headers,
        ) 