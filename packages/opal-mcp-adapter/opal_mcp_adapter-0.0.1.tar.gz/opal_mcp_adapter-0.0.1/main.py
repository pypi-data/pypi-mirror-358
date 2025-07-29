"""
MCP-Opal Adapter Service
Bidirectional adapter using proper Opal Tools SDK integration
"""

from opal_mcp_adapter.server import start


if __name__ == "__main__":
    start(host="0.0.0.0", port=8000) 