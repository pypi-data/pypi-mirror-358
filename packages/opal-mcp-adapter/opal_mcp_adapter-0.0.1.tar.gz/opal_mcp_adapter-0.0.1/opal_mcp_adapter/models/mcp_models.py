"""MCP-specific data models"""

from pydantic import BaseModel
from typing import Dict, Any, List


class MCPToolInfo(BaseModel):
    """Information about an MCP tool discovered from the server"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPDiscoveryResponse(BaseModel):
    """Response from MCP tools/list method"""
    tools: List[MCPToolInfo] 