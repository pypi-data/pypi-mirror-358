import logging

from opal_tools_sdk import tool

from ..clients.mcp_client import MCPClient
from ..models.tool_config import ToolConfiguration
from ..utils.schema_converter import json_schema_to_pydantic
from ..models.adapter_state import adapter_state

logger = logging.getLogger(__name__)


class MCPService:

    async def register_mcp_tools(self, mcp_client: MCPClient):
        # Discover tools from MCP server
        discovered_tools = await mcp_client.discover_tools()

        registered_tools = []

        for tool_info in discovered_tools:
            try:
                # Create configuration from discovered tool
                config = ToolConfiguration(
                    name=tool_info.name,
                    description=tool_info.description,
                    mcp_schema=tool_info.inputSchema,
                )

                # Generate Pydantic model from MCP schema
                model_class = json_schema_to_pydantic(
                    config.mcp_schema, f"{config.name.title()}Parameters"
                )

                # Create proxy function
                proxy_func = mcp_client.create_proxy(config, model_class)

                # Register with Opal Tools SDK using @tool decorator
                tool_decorator = tool(config.name, config.description)
                registered_func = tool_decorator(proxy_func)

                # Store for reference
                adapter_state.mcp_tools[config.name] = config
                adapter_state.dynamic_tool_functions[config.name] = registered_func

                registered_tools.append(config.name)
                logger.info(f"Configured MCP tool as Opal tool: {config.name}")

            except Exception as e:
                logger.error(f"Failed to configure tool {tool_info.name}: {str(e)}")
                # Continue with other tools even if one fails
                continue

        return discovered_tools, registered_tools
