"""
Django middleware for Spyglasses.
"""

import time
from typing import Any, Dict, List, Optional, Union

try:
    from django.http import HttpRequest, HttpResponse
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    raise ImportError(
        "Django is required to use DjangoMiddleware. "
        "Install it with: pip install 'spyglasses[django]'"
    )

from ..configuration import Configuration
from .base import BaseMiddleware, RequestInfo


class DjangoMiddleware(MiddlewareMixin, BaseMiddleware):
    """Django middleware for Spyglasses bot detection."""
    
    def __init__(
        self,
        get_response: Optional[Any] = None,
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
        Initialize Django middleware.
        
        Args:
            get_response: Django get_response callable
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
        self.get_response = get_response
        
        # Create configuration from parameters
        configuration = Configuration(
            api_key=api_key,
            debug=debug,
            collect_endpoint=collect_endpoint,
            patterns_endpoint=patterns_endpoint,
            auto_sync=auto_sync,
            platform_type=platform_type or "django",
            cache_ttl=cache_ttl,
        )
        
        # Initialize MiddlewareMixin (Django's parent class)
        MiddlewareMixin.__init__(self, get_response)
        
        # Initialize BaseMiddleware (our parent class)
        BaseMiddleware.__init__(
            self,
            configuration=configuration,
            exclude_paths=exclude_paths,
            exclude_extensions=exclude_extensions,
        )
        
        # Store start time for response time calculation
        self._request_start_times: Dict[int, float] = {}
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request through middleware chain."""
        response = self.process_request(request)
        if response:
            return response
            
        response = self.get_response(request)
        
        self.process_response(request, response)
        return response
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Process incoming request.
        
        Args:
            request: Django HttpRequest
            
        Returns:
            HttpResponse if request should be blocked, None otherwise
        """
        # Store start time
        self._request_start_times[id(request)] = time.time()
        
        # Extract request information
        request_info = self._extract_request_info(request)
        
        # Process with base middleware
        detection_result = super().process_request(request_info)
        
        # Store detection result on request for logging
        request._spyglasses_detection = detection_result
        
        # Block if necessary
        if self.should_block_request(detection_result):
            status_code, headers, body = self.create_blocked_response()
            response = HttpResponse(body, status=status_code)
            for key, value in headers.items():
                response[key] = value
            return response
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Process response and log if needed.
        
        Args:
            request: Django HttpRequest  
            response: Django HttpResponse
            
        Returns:
            Unmodified HttpResponse
        """
        # Calculate response time
        request_id = id(request)
        start_time = self._request_start_times.pop(request_id, None)
        response_time_ms = 0
        if start_time:
            response_time_ms = int((time.time() - start_time) * 1000)
        
        # Get detection result
        detection_result = getattr(request, "_spyglasses_detection", None)
        
        if detection_result and detection_result.source_type != "none":
            # Update request info with response data
            request_info = self._extract_request_info(request)
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
    
    def _extract_request_info(self, request: HttpRequest) -> RequestInfo:
        """
        Extract request information from Django request.
        
        Args:
            request: Django HttpRequest
            
        Returns:
            RequestInfo object
        """
        # Get headers as dict
        headers = {
            key: value for key, value in request.headers.items()
        }
        
        # Extract IP address
        ip_address = self.extract_ip_address(
            headers,
            getattr(request, "META", {}).get("REMOTE_ADDR", "")
        )
        
        # Build full URL
        scheme = "https" if request.is_secure() else "http"
        host = request.get_host()
        path = request.path
        query = request.META.get("QUERY_STRING", "")
        
        url = self.build_full_url(scheme, host, path, query)
        
        return RequestInfo(
            url=url,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            ip_address=ip_address,
            request_method=request.method,
            request_path=path,
            request_query=query,
            referrer=request.META.get("HTTP_REFERER"),
            headers=headers,
        ) 