# MCP Fetch Server - SSE Transport

This document explains how to use the Server-Sent Events (SSE) transport version of the MCP Fetch Server.

## Overview

The SSE transport allows the MCP Fetch Server to run as a web service that clients can connect to via HTTP+SSE, rather than using stdio transport. This is useful for:

- Running the server as a standalone web service
- Connecting multiple clients to the same server instance
- Integrating with web-based MCP clients
- Testing and development scenarios

## Installation

Install the package with SSE support:

```bash
pip install mcp-server-fetch-sse
```

## Usage

### 1. Direct SSE Transport

Run the server with direct SSE transport (similar to stdio but using SSE):

```bash
python -m mcp_server_fetch --sse
```

Or use the provided script:

```bash
mcp-server-fetch-sse
```

### 2. HTTP Server with SSE

Run the server as an HTTP service with SSE endpoints:

```bash
python -m mcp_server_fetch.http_sse_server
```

Or use the provided script:

```bash
mcp-server-fetch-http
```

#### HTTP Server Options

```bash
mcp-server-fetch-http --host 0.0.0.0 --port 8080 --user-agent "Custom Agent" --ignore-robots-txt
```

Available options:
- `--host`: Host to bind to (default: localhost)
- `--port`: Port to bind to (default: 3001)
- `--user-agent`: Custom User-Agent string
- `--ignore-robots-txt`: Ignore robots.txt restrictions
- `--proxy-url`: Proxy URL to use for requests

#### HTTP Endpoints

When running the HTTP server, the following endpoints are available:

- `GET /sse` - SSE connection endpoint
- `POST /message` - Message endpoint for client requests
- `GET /health` - Health check endpoint

### 3. Client Connection

To connect a client to the HTTP SSE server:

1. **Establish SSE connection**: Connect to `GET /sse` to establish the SSE stream
2. **Send messages**: Use `POST /message?sessionId=<session_id>` to send MCP requests
3. **Receive responses**: Responses will be sent via the SSE stream

#### Example Client Usage

```javascript
// Connect to SSE stream
const eventSource = new EventSource('http://localhost:3001/sse');

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Send a request
async function sendRequest(sessionId, request) {
    const response = await fetch(`http://localhost:3001/message?sessionId=${sessionId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request)
    });
    return response.json();
}
```

## Configuration

The SSE server supports the same configuration options as the stdio version:

- **Custom User-Agent**: Set a custom User-Agent string for requests
- **Robots.txt**: Choose whether to respect robots.txt restrictions
- **Proxy Support**: Configure proxy settings for requests

## Development

### Building from Source

```bash
cd src/fetch
pip install -e .
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest
```

## Architecture

The SSE implementation consists of three main components:

1. **`sse_server.py`**: Core SSE transport implementation using MCP SDK
2. **`http_sse_server.py`**: HTTP server wrapper for web-based deployment
3. **`__init__.py`**: Entry points for different transport modes

### Transport Modes

- **sse**: Direct SSE transport for testing
- **http+sse**: Full HTTP server with SSE endpoints

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port using `--port` option
2. **CORS issues**: Ensure your client handles CORS properly
3. **Connection drops**: The server supports automatic reconnection via session IDs

### Logging

Enable debug logging by setting the `MCP_LOG_LEVEL` environment variable:

```bash
export MCP_LOG_LEVEL=debug
mcp-server-fetch-http
```

## Security Considerations

- The HTTP server binds to localhost by default for security
- Use appropriate firewall rules when exposing to external networks
- Consider using HTTPS in production environments
- Validate session IDs to prevent unauthorized access

## Examples

### Basic Usage

```bash
# Start HTTP server
mcp-server-fetch-http --port 8080

# In another terminal, test with curl
curl -X POST "http://localhost:8080/message?sessionId=test" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### With Custom Configuration

```bash
mcp-server-fetch-http \
  --host 0.0.0.0 \
  --port 8080 \
  --user-agent "MyBot/1.0" \
  --ignore-robots-txt
``` 