"""
Type definitions for Spyglasses.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


@dataclass
class DetectionResult:
    """Result of bot or AI referrer detection."""
    
    is_bot: bool = False
    should_block: bool = False
    source_type: Literal["none", "bot", "ai_referrer"] = "none"
    matched_pattern: Optional[str] = None
    info: Optional[Union["BotInfo", "AiReferrerInfo"]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        if self.info:
            result["info"] = self.info.to_dict()
        return result


@dataclass
class BotPattern:
    """Bot pattern from API or default patterns."""
    
    pattern: str
    url: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    company: Optional[str] = None
    is_compliant: bool = False
    is_ai_model_trainer: bool = False
    intent: Optional[str] = None
    instances: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class BotInfo:
    """Bot information for detection results."""
    
    pattern: str
    type: str = "unknown"
    category: str = "Unknown"
    subcategory: str = "Unclassified"
    company: Optional[str] = None
    is_compliant: bool = False
    is_ai_model_trainer: bool = False
    intent: str = "unknown"
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AiReferrerInfo:
    """AI referrer information."""
    
    id: str
    name: str
    company: str
    url: str
    patterns: List[str] = field(default_factory=list)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class PropertySettings:
    """Property settings from API."""
    
    block_ai_model_trainers: bool = False
    custom_blocks: List[str] = field(default_factory=list)
    custom_allows: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ApiPatternResponse:
    """Response from patterns API."""
    
    version: str
    patterns: List[BotPattern] = field(default_factory=list)
    ai_referrers: List[AiReferrerInfo] = field(default_factory=list)
    property_settings: PropertySettings = field(default_factory=PropertySettings)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApiPatternResponse":
        """Create from dictionary (API response)."""
        patterns = [
            BotPattern(**pattern_data) 
            for pattern_data in data.get("patterns", [])
        ]
        
        ai_referrers = [
            AiReferrerInfo(**referrer_data)
            for referrer_data in data.get("ai_referrers", data.get("aiReferrers", []))
        ]
        
        property_settings_data = data.get("property_settings", data.get("propertySettings", {}))
        property_settings = PropertySettings(
            block_ai_model_trainers=property_settings_data.get(
                "block_ai_model_trainers", 
                property_settings_data.get("blockAiModelTrainers", False)
            ),
            custom_blocks=property_settings_data.get(
                "custom_blocks",
                property_settings_data.get("customBlocks", [])
            ),
            custom_allows=property_settings_data.get(
                "custom_allows", 
                property_settings_data.get("customAllows", [])
            ),
        )
        
        return cls(
            version=data.get("version", "1.0.0"),
            patterns=patterns,
            ai_referrers=ai_referrers,
            property_settings=property_settings,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "patterns": [p.to_dict() for p in self.patterns],
            "ai_referrers": [r.to_dict() for r in self.ai_referrers],
            "property_settings": self.property_settings.to_dict(),
        }


@dataclass
class CollectorPayload:
    """Payload for collector API."""
    
    url: str
    user_agent: str
    ip_address: str
    request_method: str
    request_path: str
    request_query: str
    response_status: int
    response_time_ms: int
    headers: Dict[str, str] = field(default_factory=dict)
    platform_type: str = "python"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None
    request_body: Optional[str] = None
    referrer: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for API submission.
        
        Note: This follows the TypeScript API schema requirements:
        - Uses camelCase for platformType
        - Omits optional fields that are None
        - Ensures required string fields are never None
        """
        payload = {
            "url": self.url,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address or "",  # Required string, never None
            "request_method": self.request_method,
            "request_path": self.request_path,
            "request_query": self.request_query or "",  # Required string, never None
            "response_status": self.response_status,
            "response_time_ms": self.response_time_ms,
            "headers": self.headers,
            "timestamp": self.timestamp,
            "platformType": self.platform_type,  # camelCase for API
            "metadata": self.metadata,
        }
        
        # Only include optional fields if they have values (not None)
        # This prevents sending null which fails TypeScript validation
        if self.request_body is not None:
            payload["request_body"] = self.request_body
        if self.referrer is not None:
            payload["referrer"] = self.referrer
            
        return payload
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict()) 