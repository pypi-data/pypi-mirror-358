"""MCP service layer for tool discovery and communication"""

import logging
from typing import List, Any, Literal, Protocol, Dict
from pydantic import BaseModel
from abc import ABC, abstractmethod

from mcp.client.streamable_http import streamablehttp_client
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession

from ..models.mcp_models import MCPToolInfo
from ..models.tool_config import ToolConfiguration

logger = logging.getLogger(__name__)


class MCPClient(Protocol):
    @abstractmethod
    async def discover_tools(self) -> List[MCPToolInfo]:
        """Discover available tools from MCP server"""
        raise NotImplementedError

    @abstractmethod
    def create_proxy(self, config: ToolConfiguration, model_class: type[BaseModel]):
        """Create a proxy function that forwards calls to MCP server"""
        raise NotImplementedError


class MCPClientHTTP:
    def __init__(self, url: str):
        self.url = url

    async def discover_tools(self) -> List[MCPToolInfo]:
        """Discover available tools from MCP server"""

        async with streamablehttp_client(self.url) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                return [
                    MCPToolInfo(**tool.model_dump(mode="json")) for tool in tools.tools
                ]

    def create_proxy(self, config: ToolConfiguration, model_class: type[BaseModel]):
        """Create a proxy function that forwards calls to MCP server"""

        async def mcp_proxy(parameters: model_class):
            """Proxy function that forwards to MCP server via JSON-RPC"""

            async with streamablehttp_client(self.url) as (
                read_stream,
                write_stream,
                _,
            ):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        config.name, parameters.model_dump(mode="json")
                    )
                    return result.content

        return mcp_proxy


class MCPClientStdio:
    def __init__(self, command: str, args: List[str], env: Dict[str, str], cwd: str):
        self.command = command
        self.args = args
        self.env = env
        self.cwd = cwd

    async def discover_tools(self) -> List[MCPToolInfo]:
        """Discover available tools from MCP server"""
        async with stdio_client(StdioServerParameters(command=self.command, args=self.args, env=self.env, cwd=self.cwd)) as (
            read,
            write,
        ):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return [
                    MCPToolInfo(**tool.model_dump(mode="json")) for tool in tools.tools
                ]


    def create_proxy(self, config: ToolConfiguration, model_class: type[BaseModel]):
        """Create a proxy function that forwards calls to MCP server"""

        async def mcp_proxy(parameters: model_class):
            """Proxy function that forwards to MCP server via JSON-RPC"""

            async with stdio_client(StdioServerParameters(command=self.command, args=self.args, env=self.env, cwd=self.cwd)) as (
                read,
                write,
            ):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        config.name, parameters.model_dump(mode="json")
                    )
                    return result.content

        return mcp_proxy
