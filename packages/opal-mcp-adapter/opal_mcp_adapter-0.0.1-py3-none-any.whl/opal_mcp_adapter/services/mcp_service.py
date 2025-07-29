"""MCP service layer for tool discovery and communication"""

import httpx
import logging
from fastapi import HTTPException
from typing import List, Any
from pydantic import BaseModel

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

from ..models.mcp_models import MCPToolInfo
from ..models.tool_config import ToolConfiguration

logger = logging.getLogger(__name__)


async def discover_mcp_tools(mcp_endpoint: str) -> List[MCPToolInfo]:
    """Discover available tools from MCP server"""

    async with streamablehttp_client(mcp_endpoint) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            return [MCPToolInfo(**tool.model_dump(mode="json")) for tool in tools.tools]


def create_mcp_proxy_function(config: ToolConfiguration, model_class: type[BaseModel]):
    """Create a proxy function that forwards calls to MCP server"""


    async def mcp_proxy(parameters: model_class):
        """Proxy function that forwards to MCP server via JSON-RPC"""

        async with streamablehttp_client(config.mcp_endpoint) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(config.name, parameters.model_dump(mode="json"))
                return result.content

    return mcp_proxy
