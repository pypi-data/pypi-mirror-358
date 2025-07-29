"""Adapter state management"""

from typing import Dict, Any


class AdapterState:
    """Global state for the adapter"""
    def __init__(self):
        self.mcp_tools: Dict[str, Any] = {}
        self.dynamic_tool_functions: Dict[str, Any] = {}

adapter_state = AdapterState()