"""
Spyglasses client for bot and AI referrer detection.
"""

import re
import threading
import time
from threading import Lock
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

import requests

from .configuration import Configuration
from .exceptions import ApiError
from .types import (
    ApiPatternResponse,
    AiReferrerInfo,
    BotInfo,
    BotPattern,
    CollectorPayload,
    DetectionResult,
)


class Client:
    """Main Spyglasses client for detection and logging."""
    
    def __init__(self, configuration: Optional[Configuration] = None) -> None:
        """
        Initialize the Spyglasses client.
        
        Args:
            configuration: Configuration instance or None for default
        """
        self.configuration = configuration or Configuration()
        self.patterns: List[BotPattern] = []
        self.ai_referrers: List[AiReferrerInfo] = []
        self._pattern_regex_cache: Dict[str, re.Pattern] = {}
        self.pattern_version = "1.0.0"
        self.last_pattern_sync = 0
        self._mutex = Lock()
        
        # Property settings loaded from API
        self._block_ai_model_trainers = False
        self._custom_blocks: List[str] = []
        self._custom_allows: List[str] = []
        
        self._load_default_patterns()
        
        # Auto-sync patterns if enabled and API key is present
        if self.configuration.is_auto_sync() and self.configuration.api_key_present():
            threading.Thread(target=self._auto_sync_patterns, daemon=True).start()
    
    def sync_patterns(self) -> Union[ApiPatternResponse, str]:
        """
        Sync patterns from the API.
        
        Returns:
            ApiPatternResponse on success, error message string on failure
        """
        if not self.configuration.api_key_present():
            message = "No API key set for pattern sync"
            self._log_debug(message)
            return message
        
        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.configuration.api_key,
            }
            
            response = requests.get(
                self.configuration.patterns_endpoint,
                headers=headers,
                timeout=30,
            )
            
            if not response.ok:
                message = f"Pattern sync HTTP error {response.status_code}: {response.reason}"
                self._log_debug(message)
                return message
            
            data = response.json()
            api_response = ApiPatternResponse.from_dict(data)
            
            # Thread-safe update of patterns
            with self._mutex:
                self.patterns = api_response.patterns
                self.ai_referrers = api_response.ai_referrers
                self.pattern_version = api_response.version
                self.last_pattern_sync = int(time.time())
                
                # Update property settings
                self._block_ai_model_trainers = api_response.property_settings.block_ai_model_trainers
                self._custom_blocks = api_response.property_settings.custom_blocks
                self._custom_allows = api_response.property_settings.custom_allows
                
                # Clear regex cache
                self._pattern_regex_cache.clear()
            
            self._log_debug(f"Synced {len(self.patterns)} patterns and {len(self.ai_referrers)} AI referrers")
            self._log_debug(f"Property settings: block_ai_model_trainers={self._block_ai_model_trainers}, "
                          f"custom_blocks={len(self._custom_blocks)}, custom_allows={len(self._custom_allows)}")
            
            return api_response
            
        except Exception as e:
            message = f"Error syncing patterns: {str(e)}"
            self._log_debug(message)
            return message
    
    def detect(self, user_agent: Optional[str], referrer: Optional[str] = None) -> DetectionResult:
        """
        Combined detection for both bot and AI referrer.
        
        Args:
            user_agent: User agent string to check
            referrer: Referrer URL to check
            
        Returns:
            DetectionResult with detection results
        """
        ua_display = f"\"{user_agent[:100]}{'...' if user_agent and len(user_agent) > 100 else ''}\"" if user_agent else "None"
        self._log_debug(f"detect() called with user_agent: {ua_display}, referrer: {referrer or 'None'}")
        
        # Check for bot first
        bot_result = self.detect_bot(user_agent)
        if bot_result.is_bot:
            self._log_debug("🤖 Final result: BOT detected, returning bot result")
            return bot_result
        
        # Check for AI referrer if provided
        if referrer:
            self._log_debug("No bot detected, starting AI referrer detection...")
            referrer_result = self.detect_ai_referrer(referrer)
            if referrer_result.source_type == "ai_referrer":
                self._log_debug("🧠 Final result: AI REFERRER detected, returning referrer result")
                return referrer_result
        else:
            self._log_debug("No referrer provided, skipping AI referrer detection")
        
        return DetectionResult()
    
    def detect_bot(self, user_agent: Optional[str]) -> DetectionResult:
        """
        Detect if a user agent is a bot.
        
        Args:
            user_agent: User agent string to check
            
        Returns:
            DetectionResult with bot detection results
        """
        if not user_agent or not user_agent.strip():
            return DetectionResult()
        
        user_agent = user_agent.strip()
        self._log_debug(f"Checking user agent: \"{user_agent[:150]}{'...' if len(user_agent) > 150 else ''}\"")
        self._log_debug(f"Testing against {len(self.patterns)} bot patterns")
        
        for pattern in self.patterns:
            try:
                regex = self._get_regex_for_pattern(pattern.pattern)
                self._log_debug(f"Testing pattern: \"{pattern.pattern}\" "
                              f"({pattern.type or 'unknown'} - {pattern.company or 'unknown company'})")
                
                if regex.search(user_agent):
                    should_block = self._should_block_pattern(pattern)
                    
                    self._log_debug(f"✅ BOT DETECTED! Pattern matched: \"{pattern.pattern}\"")
                    self._log_debug(f"Bot details: type={pattern.type}, category={pattern.category}, "
                                  f"subcategory={pattern.subcategory}, company={pattern.company}, "
                                  f"is_ai_model_trainer={pattern.is_ai_model_trainer}, should_block={should_block}")
                    
                    bot_info = BotInfo(
                        pattern=pattern.pattern,
                        type=pattern.type or "unknown",
                        category=pattern.category or "Unknown",
                        subcategory=pattern.subcategory or "Unclassified",
                        company=pattern.company,
                        is_compliant=pattern.is_compliant,
                        is_ai_model_trainer=pattern.is_ai_model_trainer,
                        intent=pattern.intent or "unknown",
                        url=pattern.url,
                    )
                    
                    return DetectionResult(
                        is_bot=True,
                        should_block=should_block,
                        source_type="bot",
                        matched_pattern=pattern.pattern,
                        info=bot_info,
                    )
                    
            except Exception as e:
                self._log_debug(f"Error with pattern {pattern.pattern}: {str(e)}")
        
        self._log_debug("No bot patterns matched user agent")
        return DetectionResult()
    
    def detect_ai_referrer(self, referrer: Optional[str]) -> DetectionResult:
        """
        Detect if a referrer is from an AI platform.
        
        Args:
            referrer: Referrer URL to check
            
        Returns:
            DetectionResult with AI referrer detection results
        """
        if not referrer or not referrer.strip():
            return DetectionResult()
        
        referrer = referrer.strip()
        self._log_debug(f"Checking referrer: \"{referrer}\"")
        
        # Extract hostname from referrer
        hostname = self._extract_hostname(referrer)
        self._log_debug(f"Extracted hostname: \"{hostname}\"")
        
        for ai_referrer in self.ai_referrers:
            self._log_debug(f"Testing AI referrer: \"{ai_referrer.name}\" ({ai_referrer.company}) "
                          f"with patterns: {', '.join(ai_referrer.patterns)}")
            
            for pattern in ai_referrer.patterns:
                self._log_debug(f"Testing AI referrer pattern: \"{pattern}\" against hostname: \"{hostname}\"")
                
                if pattern in hostname:
                    self._log_debug(f"✅ AI REFERRER DETECTED! Pattern matched: \"{pattern}\"")
                    self._log_debug(f"AI referrer details: name={ai_referrer.name}, "
                                  f"company={ai_referrer.company}, id={ai_referrer.id}")
                    
                    return DetectionResult(
                        is_bot=False,
                        should_block=False,
                        source_type="ai_referrer",
                        matched_pattern=pattern,
                        info=ai_referrer,
                    )
        
        return DetectionResult()
    
    def log_request(self, detection_result: DetectionResult, request_info: dict) -> None:
        """
        Log a request to the collector.
        
        Args:
            detection_result: Detection result from detect()
            request_info: Dictionary with request information
        """
        self._log_debug(f"log_request() called for source_type: {detection_result.source_type}")
        
        if not self.configuration.api_key_present() or detection_result.source_type == "none":
            return
        
        self._log_debug(f"Preparing to log {detection_result.source_type} event to collector")
        
        # Prepare metadata
        metadata = {"was_blocked": detection_result.should_block}
        
        if detection_result.source_type == "bot" and detection_result.info:
            bot_info = detection_result.info
            metadata.update({
                "agent_type": bot_info.type,
                "agent_category": bot_info.category,
                "agent_subcategory": bot_info.subcategory,
                "company": bot_info.company,
                "is_compliant": bot_info.is_compliant,
                "intent": bot_info.intent,
                "confidence": 0.9,
                "detection_method": "pattern_match",
            })
        elif detection_result.source_type == "ai_referrer" and detection_result.info:
            referrer_info = detection_result.info
            metadata.update({
                "source_type": "ai_referrer",
                "referrer_id": referrer_info.id,
                "referrer_name": referrer_info.name,
                "company": referrer_info.company,
            })
        
        payload = CollectorPayload(
            url=request_info.get("url", ""),
            user_agent=request_info.get("user_agent", ""),
            ip_address=request_info.get("ip_address", ""),
            request_method=request_info.get("request_method", "GET"),
            request_path=request_info.get("request_path", "/"),
            request_query=request_info.get("request_query", ""),
            referrer=request_info.get("referrer"),
            response_status=request_info.get("response_status", 403 if detection_result.should_block else 200),
            response_time_ms=request_info.get("response_time_ms", 0),
            headers=request_info.get("headers", {}),
            platform_type=self.configuration.platform_type,
            metadata=metadata,
        )
        
        # Send request in background thread to avoid blocking
        threading.Thread(
            target=self._send_collector_request,
            args=(payload, detection_result.source_type),
            daemon=True,
        ).start()
    
    def _load_default_patterns(self) -> None:
        """Load default patterns similar to the Ruby SDK."""
        self.patterns = [
            # AI Assistants
            BotPattern(
                pattern=r"ChatGPT-User\/[0-9]",
                url="https://platform.openai.com/docs/bots",
                type="chatgpt-user",
                category="AI Agent",
                subcategory="AI Assistants",
                company="OpenAI",
                is_compliant=True,
                is_ai_model_trainer=False,
                intent="UserQuery",
            ),
            BotPattern(
                pattern=r"Perplexity-User\/[0-9]",
                url="https://docs.perplexity.ai/guides/bots",
                type="perplexity-user",
                category="AI Agent",
                subcategory="AI Assistants",
                company="Perplexity AI",
                is_compliant=True,
                is_ai_model_trainer=False,
                intent="UserQuery",
            ),
            BotPattern(
                pattern=r"Gemini-User\/[0-9]",
                url="https://ai.google.dev/gemini-api/docs/bots",
                type="gemini-user",
                category="AI Agent",
                subcategory="AI Assistants",
                company="Google",
                is_compliant=True,
                is_ai_model_trainer=False,
                intent="UserQuery",
            ),
            BotPattern(
                pattern=r"Claude-User\/[0-9]",
                url="https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler",
                type="claude-user",
                category="AI Agent",
                subcategory="AI Assistants",
                company="Anthropic",
                is_compliant=True,
                is_ai_model_trainer=False,
                intent="UserQuery",
            ),
            
            # AI Model Training Crawlers
            BotPattern(
                pattern=r"CCBot\/[0-9]",
                url="https://commoncrawl.org/ccbot",
                type="ccbot",
                category="AI Crawler",
                subcategory="Model Training Crawlers",
                company="Common Crawl",
                is_compliant=True,
                is_ai_model_trainer=True,
                intent="DataCollection",
            ),
            BotPattern(
                pattern=r"ClaudeBot\/[0-9]",
                url="https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler",
                type="claude-bot",
                category="AI Crawler",
                subcategory="Model Training Crawlers",
                company="Anthropic",
                is_compliant=True,
                is_ai_model_trainer=True,
                intent="DataCollection",
            ),
            BotPattern(
                pattern=r"GPTBot\/[0-9]",
                url="https://platform.openai.com/docs/gptbot",
                type="gptbot",
                category="AI Crawler",
                subcategory="Model Training Crawlers",
                company="OpenAI",
                is_compliant=True,
                is_ai_model_trainer=True,
                intent="DataCollection",
            ),
            BotPattern(
                pattern=r"meta-externalagent\/[0-9]",
                url="https://developers.facebook.com/docs/sharing/webmasters/crawler",
                type="meta-externalagent",
                category="AI Crawler",
                subcategory="Model Training Crawlers",
                company="Meta",
                is_compliant=True,
                is_ai_model_trainer=True,
                intent="DataCollection",
            ),
            BotPattern(
                pattern=r"Applebot-Extended\/[0-9]",
                url="https://support.apple.com/en-us/119829",
                type="applebot-extended",
                category="AI Crawler",
                subcategory="Model Training Crawlers",
                company="Apple",
                is_compliant=True,
                is_ai_model_trainer=True,
                intent="DataCollection",
            ),
        ]
        
        # Default AI referrers
        self.ai_referrers = [
            AiReferrerInfo(
                id="chatgpt",
                name="ChatGPT",
                company="OpenAI",
                url="https://chat.openai.com",
                patterns=["chat.openai.com", "chatgpt.com"],
                description="Traffic from ChatGPT users clicking on links",
            ),
            AiReferrerInfo(
                id="claude",
                name="Claude",
                company="Anthropic",
                url="https://claude.ai",
                patterns=["claude.ai"],
                description="Traffic from Claude users clicking on links",
            ),
            AiReferrerInfo(
                id="perplexity",
                name="Perplexity",
                company="Perplexity AI",
                url="https://perplexity.ai",
                patterns=["perplexity.ai"],
                description="Traffic from Perplexity users clicking on links",
            ),
            AiReferrerInfo(
                id="gemini",
                name="Gemini",
                company="Google",
                url="https://gemini.google.com",
                patterns=["gemini.google.com", "bard.google.com"],
                description="Traffic from Gemini users clicking on links",
            ),
            AiReferrerInfo(
                id="copilot",
                name="Microsoft Copilot",
                company="Microsoft",
                url="https://copilot.microsoft.com/",
                patterns=["copilot.microsoft.com", "bing.com/chat"],
                description="Traffic from Microsoft Copilot users clicking on links",
            ),
        ]
    
    def _get_regex_for_pattern(self, pattern: str) -> re.Pattern:
        """Get compiled regex for pattern, using cache."""
        if pattern not in self._pattern_regex_cache:
            self._pattern_regex_cache[pattern] = re.compile(pattern, re.IGNORECASE)
        return self._pattern_regex_cache[pattern]
    
    def _should_block_pattern(self, pattern_data: BotPattern) -> bool:
        """Check if pattern should be blocked based on settings."""
        # Check if pattern is explicitly allowed
        if f"pattern:{pattern_data.pattern}" in self._custom_allows:
            return False
        
        category = pattern_data.category or "Unknown"
        subcategory = pattern_data.subcategory or "Unclassified"
        type_str = pattern_data.type or "unknown"
        
        # Check if any parent is explicitly allowed
        if (f"category:{category}" in self._custom_allows or
            f"subcategory:{category}:{subcategory}" in self._custom_allows or
            f"type:{category}:{subcategory}:{type_str}" in self._custom_allows):
            return False
        
        # Check if pattern is explicitly blocked
        if f"pattern:{pattern_data.pattern}" in self._custom_blocks:
            return True
        
        # Check if any parent is explicitly blocked
        if (f"category:{category}" in self._custom_blocks or
            f"subcategory:{category}:{subcategory}" in self._custom_blocks or
            f"type:{category}:{subcategory}:{type_str}" in self._custom_blocks):
            return True
        
        # Check for AI model trainers global setting
        if self._block_ai_model_trainers and pattern_data.is_ai_model_trainer:
            return True
        
        # Default to not blocking
        return False
    
    def _extract_hostname(self, referrer: str) -> str:
        """Extract hostname from referrer URL."""
        try:
            parsed = urlparse(referrer)
            return (parsed.hostname or referrer).lower()
        except Exception:
            return referrer.lower()
    
    def _send_collector_request(self, payload: CollectorPayload, source_type: str) -> None:
        """Send request to collector API."""
        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.configuration.api_key,
            }
            
            self._log_debug(f"Making POST request to {self.configuration.collect_endpoint}")
            payload_json = payload.to_json()
            self._log_debug(f"Payload size: {len(payload_json.encode('utf-8'))} bytes")
            
            response = requests.post(
                self.configuration.collect_endpoint,
                headers=headers,
                data=payload_json,
                timeout=10,
            )
            
            self._log_debug(f"Collector response status: {response.status_code} {response.reason}")
            
            if response.ok:
                self._log_debug(f"✅ Successfully logged {source_type} event")
            else:
                self._log_debug(f"❌ Failed to log {source_type} event")
                
        except Exception as e:
            self._log_debug(f"❌ Exception during collector request for {source_type}: {str(e)}")
    
    def _auto_sync_patterns(self) -> None:
        """Auto-sync patterns in background thread."""
        try:
            self.sync_patterns()
        except Exception as e:
            self._log_debug(f"Error syncing patterns: {str(e)}")
    
    def _log_debug(self, message: str) -> None:
        """Log debug message if debug mode is enabled."""
        if self.configuration.is_debug():
            print(f"[Spyglasses] {message}") 