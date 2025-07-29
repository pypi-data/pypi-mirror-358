"""
Base middleware class with common functionality.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from ..client import Client
from ..configuration import Configuration
from ..types import DetectionResult


@dataclass
class RequestInfo:
    """Information about an HTTP request."""
    
    url: str
    user_agent: str
    ip_address: str
    request_method: str
    request_path: str
    request_query: str = ""
    referrer: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    response_status: Optional[int] = None
    response_time_ms: Optional[int] = None


class BaseMiddleware:
    """Base middleware class for Spyglasses integrations."""
    
    # Default paths to exclude from monitoring
    DEFAULT_EXCLUDE_PATHS = [
        "/favicon.ico",
        "/robots.txt",
        "/sitemap.xml",
        "/health",
        "/status",
        "/ping",
        "/.well-known/",
        "/assets/",
        "/static/",
        "/media/",
        "/admin/jsi18n/",
        "/rails/active_storage/",
    ]
    
    # Default file extensions to exclude
    DEFAULT_EXCLUDE_EXTENSIONS = [
        ".css",
        ".js", 
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".ico",
        ".svg",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".map"
    ]
    
    def __init__(
        self,
        configuration: Optional[Configuration] = None,
        exclude_paths: Optional[List[Union[str, object]]] = None,
        exclude_extensions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize base middleware.
        
        Args:
            configuration: Spyglasses configuration
            exclude_paths: Additional paths to exclude
            exclude_extensions: Additional file extensions to exclude
        """
        self.configuration = configuration or Configuration()
        self.client = Client(self.configuration)
        
        # Combine default and custom exclusions
        self.exclude_paths = self.DEFAULT_EXCLUDE_PATHS.copy()
        if exclude_paths:
            self.exclude_paths.extend(str(path) for path in exclude_paths)
        
        self.exclude_extensions = self.DEFAULT_EXCLUDE_EXTENSIONS.copy()  
        if exclude_extensions:
            self.exclude_extensions.extend(exclude_extensions)
    
    def should_exclude_request(self, request_path: str) -> bool:
        """
        Check if a request should be excluded from monitoring.
        
        Args:
            request_path: The request path to check
            
        Returns:
            True if the request should be excluded
        """
        # Check against excluded paths
        for exclude_path in self.exclude_paths:
            if request_path.startswith(exclude_path):
                return True
        
        # Check against excluded file extensions
        for ext in self.exclude_extensions:
            if request_path.endswith(ext):
                return True
        
        return False
    
    def process_request(self, request_info: RequestInfo) -> DetectionResult:
        """
        Process a request and return detection results.
        
        Args:
            request_info: Information about the request
            
        Returns:
            DetectionResult from detection
        """
        if self.should_exclude_request(request_info.request_path):
            return DetectionResult()
        
        # Perform detection
        detection_result = self.client.detect(
            user_agent=request_info.user_agent,
            referrer=request_info.referrer,
        )
        
        # Log the request if something was detected
        if detection_result.source_type != "none":
            # Convert RequestInfo to dict for log_request
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
        
        return detection_result
    
    def should_block_request(self, detection_result: DetectionResult) -> bool:
        """
        Check if a request should be blocked based on detection results.
        
        Args:
            detection_result: Results from detection
            
        Returns:
            True if the request should be blocked
        """
        return detection_result.should_block
    
    def create_blocked_response(self) -> tuple:
        """
        Create a response for blocked requests.
        
        Returns:
            Tuple of (status_code, headers, body)
        """
        return (
            403,
            {"Content-Type": "text/plain"},
            "Access Denied"
        )
    
    def extract_ip_address(self, headers: Dict[str, str], remote_addr: str = "") -> str:
        """
        Extract the real IP address from request headers.
        
        Args:
            headers: Request headers
            remote_addr: Remote address from server
            
        Returns:
            Best guess at real IP address
        """
        # Try common headers used by proxies and load balancers
        ip_headers = [
            "X-Forwarded-For",
            "X-Real-IP",
            "X-Client-IP",
            "CF-Connecting-IP",  # Cloudflare
            "X-Forwarded",
            "Forwarded-For",
            "Forwarded",
        ]
        
        for header in ip_headers:
            value = headers.get(header, headers.get(header.lower(), ""))
            if value:
                # X-Forwarded-For can contain multiple IPs, take the first
                ip = value.split(",")[0].strip()
                if ip:
                    return ip
        
        return remote_addr or ""
    
    def build_full_url(self, scheme: str, host: str, path: str, query: str = "") -> str:
        """
        Build full URL from components.
        
        Args:
            scheme: URL scheme (http/https)
            host: Host header
            path: Request path
            query: Query string
            
        Returns:
            Full URL
        """
        url = f"{scheme}://{host}{path}"
        if query:
            url += f"?{query}"
        return url 