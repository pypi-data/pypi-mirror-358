# MCP-Opal Adapter

A bidirectional adapter service that converts between MCP (Model Context Protocol) tools and Opal tools using the official Opal Tools SDK with automatic MCP discovery.

## Quick start

Install the opal-mcp-adapter cli

```bash
pip install opal-mcp-adapter
```

Start the mcp adapter with an mcp config
```bash
opal-mcp-adapter --port 8030 --config mcp.json
```

You can now see the MCP tools registered as Opal tools at

`http://localhost:8030/discovery`

and use them inside Opal


## Usage

### Using a config file

The adapter supports standard `mcp.json` files as a config argument

A sample mcp.json

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Desktop",
        "/Users/username/Downloads"
      ]
    }
  }
}
```

In order to run these mcp tools through the adapter, it needs to be pointed towards the config file

```bash
opal-mcp-adapter --config mcp.json
```

This will register the servers defined in the config file, and launch a compatible opal tools server at "http://localhost:8000" (with the default host and port)


See more mcp.json examples here
https://modelcontextprotocol.io/quickstart/user

### CLI Usage Examples

The `opal-mcp-adapter` command supports various options for customizing the server behavior:

```bash
# Start server on 0.0.0.0:8000 (default)
opal-mcp-adapter

# Start server on localhost:8000
opal-mcp-adapter --host localhost

# Start server on 0.0.0.0:9000
opal-mcp-adapter --port 9000

# Start server on 127.0.0.1:8080
opal-mcp-adapter --host 127.0.0.1 --port 8080

# Start server with MCP configuration file
opal-mcp-adapter --config mcp.json

# Start server on custom port with config
opal-mcp-adapter --port 8030 --config mcp.json

# Display version information
opal-mcp-adapter --version
```

#### Command Line Options

- `--host`: Host address to bind the server to (default: 0.0.0.0)
- `--port`: Port number to bind the server to (default: 8000)
- `--config`: Path to the MCP configuration file
- `--version`: Display version information and exit

#### Port Validation

The CLI validates that the port number is within the valid range (1-65535). If an invalid port is specified, the command will exit with an error message.

## API Usage Examples

The MCP-Opal adapter provides a REST API for dynamic tool registration and management. All endpoints return JSON responses.

### Register MCP Tools

#### POST /register

Register MCP tools by discovering them from an MCP server via HTTP transport.

**Request Body:**
```json
{
  "transport": "http",
  "url": "http://localhost:3000"
}
```

**Example using curl:**
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "transport": "http",
    "url": "http://localhost:3000"
  }'
```

**Response:**
```json
{
  "status": "registered",
  "tools": ["tool1", "tool2", "tool3"],
  "total_discovered": 3,
  "successfully_registered": 3
}
```

**Error Response (400):**
```json
{
  "detail": "Failed to discover tools from http://localhost:3000: Connection refused"
}
```

### Health Check

#### GET /health

Check the health status of the adapter service.

**Example using curl:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "mcp_tools_count": 5,
  "opal_tools_count": 5
}
```

### Get Adapter Status

#### GET /status

Get detailed status and configuration information.

**Example using curl:**
```bash
curl http://localhost:8000/status
```

**Response:**
```json
{
  "mcp_tools": ["filesystem_read", "filesystem_write", "web_search"],
  "opal_tools": ["filesystem_read", "filesystem_write", "web_search"],
  "opal_discovery_url": "/discovery"
}
```

### Remove a Tool

#### DELETE /tools/{tool_name}

Remove a configured tool from the adapter.

**Example using curl:**
```bash
curl -X DELETE http://localhost:8000/tools/filesystem_read
```

**Response:**
```json
{
  "status": "removed",
  "tool": "filesystem_read"
}
```

**Error Response (404):**
```json
{
  "detail": "Tool not found"
}
```

### Complete API Workflow Example

Here's a complete example of registering and using MCP tools:

```bash
# 1. Start the adapter server
opal-mcp-adapter --port 8000

# 2. Register MCP tools from a server
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "transport": "http",
    "url": "http://localhost:3000"
  }'

# 3. Check health status
curl http://localhost:8000/health

# 4. View registered tools
curl http://localhost:8000/status

# 5. Access Opal tools discovery endpoint
curl http://localhost:8000/discovery

# 6. Remove a tool when no longer needed
curl -X DELETE http://localhost:8000/tools/tool_name
```

## Key Features

- **MCP Discovery**: Automatically discovers tools from MCP servers
- **Proper Opal Tools SDK Integration**: Uses `ToolsService` and `@tool` decorator
- **Dynamic Schema Translation**: JSON Schema to Pydantic model conversion
- **JSON-RPC Proxy**: Forwards MCP calls via JSON-RPC protocol
- **Discovery Endpoint**: Exposes `/discovery` for tool listing
- **Just-in-Time Configuration**: HTTP API for dynamic tool registration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HTTP Configuration API                   │
│           POST /register  (MCP endpoint only)               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 MCP-Opal Proxy Service                      │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │   MCP Discovery │◄──►│   Opal Tools    │                 │
│  │   (tools/list)  │    │   SDK           │                 │
│  └─────────────────┘    └─────────────────┘                 │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │  Dynamic Tool   │    │  Protocol       │                 │
│  │  Registry       │    │  Translator     │                 │
│  └─────────────────┘    └─────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```


### Opal Tools Endpoints

#### GET /discovery
Discover available Opal tools (auto-generated by Opal Tools SDK).

#### POST /tools/{tool_name}
Call a configured tool via Opal interface.

**Request Body:**
```json
{
  "param1": "value1",
  "param2": 42
}
```

### Management Endpoints

#### GET /health
Health check endpoint.

#### GET /status
Get adapter status and configuration.

#### DELETE /configure/{tool_name}
Remove a configured tool.

## MCP Discovery Process

The adapter automatically:

1. **Discovers Tools**: Calls `tools/list` on the MCP server
2. **Extracts Schemas**: Gets tool names, descriptions, and input schemas
3. **Converts Schemas**: Transforms JSON Schema to Pydantic models
4. **Creates Proxies**: Generates proxy functions for each tool
5. **Registers Tools**: Registers them with the Opal Tools SDK

### MCP Protocol Support

The adapter supports the standard MCP protocol:

- **tools/list**: Discovers available tools
- **tools/call**: Executes tool calls via JSON-RPC
- **server/health**: Health checking (optional)

##

## Error Handling

### Network Errors
- Connection timeouts (30s default)
- MCP server unavailability
- JSON-RPC protocol errors

### Validation Errors
- Schema validation failures via Pydantic
- Required field missing
- Type conversion errors

### Discovery Errors
- MCP server discovery failures
- Invalid tool schemas
- Duplicate tool names

## Monitoring

### Health Checks
- Service availability
- Tool count monitoring
- Configuration status

### Logging
- Structured logging throughout
- Error tracking
- Performance monitoring

## Security Considerations

### Input Validation
- Schema-based validation via Pydantic
- Type checking and conversion
- Required field enforcement

### Network Security
- Timeout configuration
- Error message sanitization
- Connection pooling

## Future Enhancements

### Planned Features
- Authentication and authorization
- Rate limiting
- Caching layer
- Metrics collection
- WebSocket support
- GraphQL interface

### Scalability Improvements
- Database persistence
- Load balancing
- Service discovery
- Circuit breaker pattern

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.