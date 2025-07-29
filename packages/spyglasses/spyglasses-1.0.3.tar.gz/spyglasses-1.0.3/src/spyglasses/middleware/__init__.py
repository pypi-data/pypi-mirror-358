"""
Middleware integrations for various Python web frameworks.
"""

# Core middleware utilities
from .base import BaseMiddleware, RequestInfo

# Framework-specific middleware
try:
    from .django import DjangoMiddleware
except ImportError:
    DjangoMiddleware = None

try:
    from .flask import FlaskMiddleware
except ImportError:
    FlaskMiddleware = None

try:
    from .fastapi import FastAPIMiddleware
except ImportError:
    FastAPIMiddleware = None

# WSGI/ASGI middleware
from .wsgi import WSGIMiddleware
try:
    from .asgi import ASGIMiddleware
except ImportError:
    ASGIMiddleware = None

__all__ = [
    "BaseMiddleware",
    "RequestInfo", 
    "DjangoMiddleware",
    "FlaskMiddleware",
    "FastAPIMiddleware",
    "WSGIMiddleware",
    "ASGIMiddleware",
] 