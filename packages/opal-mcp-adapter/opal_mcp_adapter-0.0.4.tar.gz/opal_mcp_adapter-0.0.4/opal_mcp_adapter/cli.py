#!/usr/bin/env python3
"""
CLI for the MCP-Opal Adapter Service
"""

import argparse
import sys
import json
import os
import asyncio
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

from .server import start
from .services.mcp_service import MCPService
from .clients.mcp_client import MCPClientStdio


class MCPJSONConfig(BaseModel):
    class Server(BaseModel):
        command: str
        args: List[str] = Field(default=[])
        env: Dict[str, str] = Field(default={})
        cwd: str = Field(default_factory=lambda: os.getcwd())

    mcpServers: Dict[str, Server]


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="MCP-Opal Adapter Service - Bidirectional adapter for converting between MCP and Opal tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  opal-mcp-adapter                    # Start server on 0.0.0.0:8000 (default)
  opal-mcp-adapter --host localhost   # Start server on localhost:8000
  opal-mcp-adapter --port 9000        # Start server on 0.0.0.0:9000
  opal-mcp-adapter --host 127.0.0.1 --port 8080  # Start server on 127.0.0.1:8080
        """,
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host address to bind the server to (default: 0.0.0.0)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number to bind the server to (default: 8000)",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to the MCP configuration file",
    )

    parser.add_argument("--version", action="version", version="opal-mcp-adapter 0.0.4")

    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate command line arguments."""
    if args.port < 1 or args.port > 65535:
        print(
            f"Error: Port must be between 1 and 65535, got {args.port}", file=sys.stderr
        )
        sys.exit(1)


async def register_mcp_config(file_path: str) -> None:
    """Register the MCP configuration file."""
    with open(file_path, "r") as file:
        config = MCPJSONConfig.model_validate_json(file.read())

        mcp_service = MCPService()
        for name, server in config.mcpServers.items():
            mcp_client = MCPClientStdio(
                server.command, server.args, server.env, server.cwd
            )

            discovered_tools, registered_tools = await mcp_service.register_mcp_tools(
                mcp_client
            )

            print(f"MCP Server {name} discovered {len(discovered_tools)} tools and registered {len(registered_tools)} tools")


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    validate_args(args)

    print(f"Starting MCP-Opal Adapter Service on {args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")

    if args.config:
        asyncio.run(register_mcp_config(args.config))

    try:
        start(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
