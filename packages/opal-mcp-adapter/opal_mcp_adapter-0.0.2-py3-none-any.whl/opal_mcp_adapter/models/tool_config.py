"""Tool configuration models"""

from pydantic import BaseModel
from typing import Dict, Any


class ToolConfiguration(BaseModel):
    """Configuration for MCP tools to be exposed as Opal tools"""
    name: str
    description: str
    mcp_schema: Dict[str, Any]