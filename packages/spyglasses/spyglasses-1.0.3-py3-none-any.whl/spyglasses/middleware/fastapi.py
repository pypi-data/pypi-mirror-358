"""
FastAPI middleware for Spyglasses.
"""

import time
from typing import Any, Dict, List, Optional, Union

try:
    from fastapi import FastAPI, Request, Response, HTTPException
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import PlainTextResponse
except ImportError:
    raise ImportError(
        "FastAPI and Starlette are required to use FastAPIMiddleware. "
        "Install them with: pip install 'spyglasses[fastapi]'"
    )

from ..configuration import Configuration
from .base import BaseMiddleware, RequestInfo


class FastAPIMiddleware(BaseHTTPMiddleware, BaseMiddleware):
    """FastAPI middleware for Spyglasses bot detection."""
    
    def __init__(
        self,
        app: FastAPI,
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
        Initialize FastAPI middleware.
        
        Args:
            app: FastAPI application instance
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
            platform_type=platform_type or "fastapi",
            cache_ttl=cache_ttl,
        )
        
        # Initialize base middleware
        BaseMiddleware.__init__(
            self,
            configuration=configuration,
            exclude_paths=exclude_paths,
            exclude_extensions=exclude_extensions,
        )
        
        # Initialize Starlette middleware
        BaseHTTPMiddleware.__init__(self, app)
    
    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """
        Process request through middleware.
        
        Args:
            request: Starlette Request
            call_next: Next middleware/route handler
            
        Returns:
            Response
        """
        # Store start time
        start_time = time.time()
        
        # Extract request information
        request_info = await self._extract_request_info(request)
        
        # Process with base middleware
        detection_result = super().process_request(request_info)
        
        # Block if necessary
        if self.should_block_request(detection_result):
            status_code, headers, body = self.create_blocked_response()
            return PlainTextResponse(
                content=body,
                status_code=status_code,
                headers=headers,
            )
        
        # Continue to next middleware/handler
        response = await call_next(request)
        
        # Log if needed
        if detection_result and detection_result.source_type != "none":
            # Calculate response time
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
    
    async def _extract_request_info(self, request: Request) -> RequestInfo:
        """
        Extract request information from FastAPI/Starlette request.
        
        Args:
            request: Starlette Request
            
        Returns:
            RequestInfo object
        """
        # Get headers as dict
        headers = dict(request.headers)
        
        # Extract IP address
        ip_address = self.extract_ip_address(
            headers,
            request.client.host if request.client else ""
        )
        
        # Build full URL
        url = str(request.url)
        
        return RequestInfo(
            url=url,
            user_agent=request.headers.get("user-agent", ""),
            ip_address=ip_address,
            request_method=request.method,
            request_path=request.url.path,
            request_query=request.url.query or "",
            referrer=request.headers.get("referer"),
            headers=headers,
        )


def setup_spyglasses(
    app: FastAPI,
    api_key: Optional[str] = None,
    debug: Optional[bool] = None,
    collect_endpoint: Optional[str] = None,
    patterns_endpoint: Optional[str] = None,
    auto_sync: Optional[bool] = None,
    platform_type: Optional[str] = None,
    cache_ttl: Optional[int] = None,
    exclude_paths: Optional[List[Union[str, object]]] = None,
    exclude_extensions: Optional[List[str]] = None,
) -> FastAPIMiddleware:
    """
    Setup Spyglasses middleware for FastAPI app.
    
    Args:
        app: FastAPI application instance
        api_key: Spyglasses API key
        debug: Enable debug logging
        collect_endpoint: Custom collector endpoint
        patterns_endpoint: Custom patterns endpoint
        auto_sync: Auto-sync patterns on startup
        platform_type: Platform identifier
        cache_ttl: Pattern cache TTL in seconds
        exclude_paths: Paths to exclude from monitoring
        exclude_extensions: File extensions to exclude
        
    Returns:
        FastAPIMiddleware instance
    """
    middleware = FastAPIMiddleware(
        app=app,
        api_key=api_key,
        debug=debug,
        collect_endpoint=collect_endpoint,
        patterns_endpoint=patterns_endpoint,
        auto_sync=auto_sync,
        platform_type=platform_type,
        cache_ttl=cache_ttl,
        exclude_paths=exclude_paths,
        exclude_extensions=exclude_extensions,
    )
    
    app.add_middleware(FastAPIMiddleware, **{
        'api_key': api_key,
        'debug': debug,
        'collect_endpoint': collect_endpoint,
        'patterns_endpoint': patterns_endpoint,
        'auto_sync': auto_sync,
        'platform_type': platform_type,
        'cache_ttl': cache_ttl,
        'exclude_paths': exclude_paths,
        'exclude_extensions': exclude_extensions,
    })
    
    return middleware 