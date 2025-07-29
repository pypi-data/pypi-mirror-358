"""API routes for MCP-Opal adapter"""

import logging
from fastapi import APIRouter, HTTPException
from opal_tools_sdk import tool

from ..models.tool_config import ToolConfiguration
from ..models.adapter_state import AdapterState
from ..services.mcp_service import discover_mcp_tools, create_mcp_proxy_function
from ..utils.schema_converter import json_schema_to_pydantic

logger = logging.getLogger(__name__)

router = APIRouter()
adapter_state = AdapterState()


@router.post("/configure")
async def configure_mcp_tools(mcp_endpoint: str):
    """Configure MCP tools by discovering them from the MCP server"""
    
    try:
        # Discover tools from MCP server
        discovered_tools = await discover_mcp_tools(mcp_endpoint)
        
        configured_tools = []
        
        for tool_info in discovered_tools:
            try:
                # Create configuration from discovered tool
                config = ToolConfiguration(
                    name=tool_info.name,
                    description=tool_info.description,
                    mcp_schema=tool_info.inputSchema,
                    mcp_endpoint=mcp_endpoint
                )
                
                # Generate Pydantic model from MCP schema
                model_class = json_schema_to_pydantic(
                    config.mcp_schema,
                    f"{config.name.title()}Parameters"
                )
                
                # Create proxy function
                proxy_func = create_mcp_proxy_function(config, model_class)
                
                # Register with Opal Tools SDK using @tool decorator
                tool_decorator = tool(config.name, config.description)
                registered_func = tool_decorator(proxy_func)
                
                # Store for reference
                adapter_state.mcp_tools[config.name] = config
                adapter_state.dynamic_tool_functions[config.name] = registered_func
                
                configured_tools.append(config.name)
                logger.info(f"Configured MCP tool as Opal tool: {config.name}")
                
            except Exception as e:
                logger.error(
                    f"Failed to configure tool {tool_info.name}: {str(e)}"
                )
                # Continue with other tools even if one fails
                continue
        
        return {
            "status": "configured", 
            "tools": configured_tools,
            "total_discovered": len(discovered_tools),
            "successfully_configured": len(configured_tools)
        }
        
    except Exception as e:
        logger.error(
            f"Failed to discover tools from {mcp_endpoint}: {str(e)}"
        )
        raise HTTPException(
            status_code=400,
            detail=(
                f"Failed to discover tools from {mcp_endpoint}: {str(e)}"
            )
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mcp_tools_count": len(adapter_state.mcp_tools),
        "opal_tools_count": len(adapter_state.dynamic_tool_functions)
    }


@router.get("/status")
async def get_status():
    """Get adapter status and configuration"""
    return {
        "mcp_tools": list(adapter_state.mcp_tools.keys()),
        "opal_tools": list(adapter_state.dynamic_tool_functions.keys()),
        "opal_discovery_url": "/discovery"
    }


@router.delete("/configure/{tool_name}")
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