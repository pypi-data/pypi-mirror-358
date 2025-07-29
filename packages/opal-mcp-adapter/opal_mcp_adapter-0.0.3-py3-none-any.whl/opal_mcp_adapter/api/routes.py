"""API routes for MCP-Opal adapter"""

import logging
from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models.adapter_state import adapter_state
from ..services.mcp_service import MCPService
from ..clients.mcp_client import MCPClientHTTP

logger = logging.getLogger(__name__)

router = APIRouter()


class RegisterRequest(BaseModel):
    """Request body for registering MCP tools"""
    transport: Literal["http"] = "http"
    url: str


@router.post("/register")
async def register(request: RegisterRequest):
    """Register MCP tools by discovering them from the MCP server"""

    try:
        mcp_client = MCPClientHTTP(request.url)
        discovered_tools, registered_tools = await MCPService().register_mcp_tools(
            mcp_client
        )

        return {
            "status": "registered",
            "tools": registered_tools,
            "total_discovered": len(discovered_tools),
            "successfully_registered": len(registered_tools),
        }

    except Exception as e:
        logger.error(f"Failed to discover tools from {request.url}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=(f"Failed to discover tools from {request.url}: {str(e)}"),
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mcp_tools_count": len(adapter_state.mcp_tools),
        "opal_tools_count": len(adapter_state.dynamic_tool_functions),
    }


@router.get("/status")
async def get_status():
    """Get adapter status and configuration"""
    return {
        "mcp_tools": list(adapter_state.mcp_tools.keys()),
        "opal_tools": list(adapter_state.dynamic_tool_functions.keys()),
        "opal_discovery_url": "/discovery",
    }


@router.delete("/tools/{tool_name}")
async def remove_tool(tool_name: str):
    """Remove a configured tool"""
    removed = False

    if tool_name in adapter_state.mcp_tools:
        del adapter_state.mcp_tools[tool_name]
        removed = True

    if tool_name in adapter_state.dynamic_tool_functions:
        del adapter_state.dynamic_tool_functions[tool_name]
        removed = True

    if not removed:
        raise HTTPException(status_code=404, detail="Tool not found")

    logger.info(f"Removed tool: {tool_name}")
    return {"status": "removed", "tool": tool_name}
