"""
MCP-Opal Adapter Service
Bidirectional adapter using proper Opal Tools SDK integration
"""

__version__ = "1.0.0"

from .server import start
from .cli import main

__all__ = ["start", "main", "__version__"]