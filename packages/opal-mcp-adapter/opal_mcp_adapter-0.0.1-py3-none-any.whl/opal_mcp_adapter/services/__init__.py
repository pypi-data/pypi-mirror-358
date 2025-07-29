"""Service layer for MCP-Opal adapter"""

from .mcp_service import discover_mcp_tools, create_mcp_proxy_function

__all__ = [
    "discover_mcp_tools",
    "create_mcp_proxy_function"
] 