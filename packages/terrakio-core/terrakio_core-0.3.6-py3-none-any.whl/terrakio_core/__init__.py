# terrakio_core/__init__.py
"""
Terrakio Core

Core components for Terrakio API clients.
"""

__version__ = "0.3.4"

from .async_client import AsyncClient
from .sync_client import SyncClient

__all__ = [
    "AsyncClient", 
    "SyncClient"
]