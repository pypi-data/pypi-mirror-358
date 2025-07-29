# MCP-Opal Adapter - Project Structure

This document describes the organized folder structure of the MCP-Opal adapter service.

## Overview

The project has been reorganized from a monolithic `main.py` file into a well-structured package with clear separation of concerns.

## Directory Structure

```
tools/mcp-adapter/
├── src/                          # Main source code
│   ├── __init__.py              # Package initialization
│   ├── app.py                   # FastAPI application setup
│   ├── api/                     # API layer
│   │   ├── __init__.py
│   │   └── routes.py            # FastAPI route definitions
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── mcp_models.py        # MCP-specific models
│   │   ├── tool_config.py       # Tool configuration models
│   │   └── adapter_state.py     # Adapter state management
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   └── mcp_service.py       # MCP communication services
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   └── schema_converter.py  # JSON Schema to Pydantic conversion
│   └── config/                  # Configuration management
│       ├── __init__.py
│       └── settings.py          # Application settings
├── main.py                      # Application entry point
├── pyproject.toml               # Python project configuration and dependencies
├── uv.lock                      # Locked dependency versions for reproducible builds
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose setup
├── Makefile                     # Build and development commands
├── README.md                    # Main documentation
└── examples/                    # Example configurations
```

## Module Descriptions

### `src/app.py`
- Main FastAPI application setup
- Integrates Opal Tools SDK
- Configures logging and middleware

### `src/api/routes.py`
- FastAPI route definitions
- HTTP endpoint handlers
- Request/response processing

### `src/models/`
- **`mcp_models.py`**: MCP-specific data structures (MCPToolInfo, MCPDiscoveryResponse)
- **`tool_config.py`**: Tool configuration models
- **`adapter_state.py`**: Global adapter state management

### `src/services/mcp_service.py`
- MCP server communication logic
- Tool discovery functionality
- Proxy function creation

### `src/utils/schema_converter.py`
- JSON Schema to Pydantic model conversion
- Type mapping utilities
- Dynamic model generation

### `src/config/settings.py`
- Application configuration management
- Environment variable handling
- Default settings

## Benefits of This Structure

1. **Separation of Concerns**: Each module has a single responsibility
2. **Maintainability**: Easier to locate and modify specific functionality
3. **Testability**: Individual components can be tested in isolation
4. **Scalability**: Easy to add new features without affecting existing code
5. **Readability**: Clear organization makes the codebase easier to understand

## Usage

The application can still be run the same way:

```bash
# Install dependencies using uv
uv sync

# Run the application
python main.py

# Or using uvicorn directly
uvicorn src.app:app --host 0.0.0.0 --port 8000
```

## Development

When adding new features:

1. **New API endpoints**: Add to `src/api/routes.py`
2. **New data models**: Add to appropriate file in `src/models/`
3. **New business logic**: Add to `src/services/`
4. **New utilities**: Add to `src/utils/`
5. **Configuration changes**: Modify `src/config/settings.py`

## Testing

The modular structure makes it easy to test individual components:

```python
# Example: Test MCP service
from src.services.mcp_service import discover_mcp_tools

# Example: Test schema conversion
from src.utils.schema_converter import json_schema_to_pydantic
``` 