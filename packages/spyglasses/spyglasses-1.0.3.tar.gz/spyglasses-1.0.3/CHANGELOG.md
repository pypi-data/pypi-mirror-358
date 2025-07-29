# Changelog

All notable changes to the Spyglasses Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.3] - 2025-06-26

### Fixed
- Broken links to Github repos
- Standardized the README overview across plugins

## [1.0.0] - 2025-06-25

### Added
- Initial release of Spyglasses Python SDK
- Core bot and AI referrer detection capabilities
- Support for Django, Flask, FastAPI, WSGI, and ASGI frameworks
- Pattern synchronization from Spyglasses API
- Request logging to Spyglasses collector
- Comprehensive type hints and documentation
- Thread-safe implementation
- Configurable exclusion rules for paths and file extensions
- Custom blocking and allowing rules
- Background pattern auto-sync
- Debug logging capabilities

### Framework Support
- **Django**: Complete middleware integration with Django's middleware system
- **Flask**: Middleware and decorator support for route-level protection
- **FastAPI**: Async middleware integration with Starlette
- **WSGI**: Universal WSGI middleware for any WSGI-compliant application
- **ASGI**: Universal ASGI middleware for modern async applications

### Detection Capabilities
- AI Assistant detection (ChatGPT-User, Claude-User, Perplexity-User, Gemini-User)
- AI Training Crawler detection (GPTBot, ClaudeBot, CCBot, meta-externalagent, Applebot-Extended)
- AI Referrer detection (traffic from ChatGPT, Claude, Perplexity, Gemini, Copilot)
- Custom pattern matching with regex support
- Configurable blocking rules based on bot categories and types
