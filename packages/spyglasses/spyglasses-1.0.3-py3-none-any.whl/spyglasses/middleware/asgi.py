"""
ASGI middleware for Spyglasses.
"""

import asyncio
import time
from typing import Any, Callable, Dict, List, Optional, Union

from ..configuration import Configuration
from .base import BaseMiddleware, RequestInfo


class ASGIMiddleware(BaseMiddleware):
    """ASGI middleware for Spyglasses bot detection."""
    
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
        Initialize ASGI middleware.
        
        Args:
            app: ASGI application callable
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
            platform_type=platform_type or "asgi",
            cache_ttl=cache_ttl,
        )
        
        # Initialize base middleware
        super().__init__(
            configuration=configuration,
            exclude_paths=exclude_paths,
            exclude_extensions=exclude_extensions,
        )
    
    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
        """
        ASGI application interface.
        
        Args:
            scope: ASGI scope dict
            receive: ASGI receive callable
            send: ASGI send callable
        """
        # Only handle HTTP requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Store start time
        start_time = time.time()
        
        # Extract request information
        request_info = self._extract_request_info(scope)
        
        # Process with base middleware
        detection_result = super().process_request(request_info)
        
        # Block if necessary
        if self.should_block_request(detection_result):
            await self._send_blocked_response(send)
            return
        
        # Capture response for logging
        captured_response = {"status": None}
        
        async def capture_send(message: Dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                captured_response["status"] = message.get("status", 200)
            await send(message)
        
        # Call original app
        await self.app(scope, receive, capture_send)
        
        # Log if needed (run in background to avoid blocking)
        if detection_result and detection_result.source_type != "none":
            asyncio.create_task(self._log_request_async(
                detection_result,
                request_info,
                captured_response.get("status", 200),
                int((time.time() - start_time) * 1000)
            ))
    
    async def _send_blocked_response(self, send: Callable) -> None:
        """Send blocked response."""
        status_code, headers, body = self.create_blocked_response()
        
        await send({
            "type": "http.response.start",
            "status": status_code,
            "headers": [[key.encode(), value.encode()] for key, value in headers.items()],
        })
        
        await send({
            "type": "http.response.body",
            "body": body.encode('utf-8'),
        })
    
    async def _log_request_async(
        self,
        detection_result,
        request_info: RequestInfo,
        status_code: int,
        response_time_ms: int
    ) -> None:
        """Log request asynchronously."""
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
        
        # Run in thread pool to avoid blocking async loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self.client.log_request,
            detection_result,
            request_dict
        )
    
    def _extract_request_info(self, scope: Dict[str, Any]) -> RequestInfo:
        """
        Extract request information from ASGI scope.
        
        Args:
            scope: ASGI scope dict
            
        Returns:
            RequestInfo object
        """
        # Extract headers from scope
        headers = {}
        for header_tuple in scope.get("headers", []):
            name = header_tuple[0].decode('latin1')
            value = header_tuple[1].decode('latin1')
            headers[name.title()] = value
        
        # Extract IP address
        client = scope.get("client", ["", 0])
        remote_addr = client[0] if client else ""
        
        ip_address = self.extract_ip_address(headers, remote_addr)
        
        # Build full URL
        scheme = scope.get("scheme", "http")
        server = scope.get("server", ["localhost", 80])
        server_name = server[0]
        server_port = server[1]
        
        # Build host
        if (scheme == 'https' and server_port == 443) or (scheme == 'http' and server_port == 80):
            host = server_name
        else:
            host = f"{server_name}:{server_port}"
        
        path = scope.get("path", "/")
        query = scope.get("query_string", b"").decode('latin1')
        
        url = self.build_full_url(scheme, host, path, query)
        
        return RequestInfo(
            url=url,
            user_agent=headers.get("User-Agent", ""),
            ip_address=ip_address,
            request_method=scope.get("method", "GET"),
            request_path=path,
            request_query=query,
            referrer=headers.get("Referer"),
            headers=headers,
        ) 