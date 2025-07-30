import asyncio
import json
import os
from typing import Dict, Optional

from aiohttp import web
from mcp.server.sse import SSEServerTransport
from mcp_server_fetch.sse_server import serve_sse


class FetchSSEServer:
    def __init__(
        self,
        custom_user_agent: Optional[str] = None,
        ignore_robots_txt: bool = False,
        proxy_url: Optional[str] = None,
    ):
        self.custom_user_agent = custom_user_agent
        self.ignore_robots_txt = ignore_robots_txt
        self.proxy_url = proxy_url
        self.transports: Dict[str, SSEServerTransport] = {}

    async def handle_sse(self, request: web.Request) -> web.Response:
        """Handle SSE connection requests."""
        transport: SSEServerTransport
        session_id = request.query.get("sessionId")

        if session_id and session_id in self.transports:
            # Reuse existing transport
            transport = self.transports[session_id]
            print(f"Client reconnecting with session ID: {session_id}")
        else:
            # Create new transport for new session
            transport = SSEServerTransport("/message", request)
            self.transports[transport.session_id] = transport
            print(f"New client connected with session ID: {transport.session_id}")

            # Set up cleanup when transport closes
            transport.onclose = lambda: self._cleanup_transport(transport.session_id)

        return await transport.handle_request(request)

    async def handle_message(self, request: web.Request) -> web.Response:
        """Handle POST messages from clients."""
        session_id = request.query.get("sessionId")
        if not session_id or session_id not in self.transports:
            return web.json_response(
                {"error": "Invalid session ID"}, status=400
            )

        transport = self.transports[session_id]
        return await transport.handle_post_message(request, request)

    def _cleanup_transport(self, session_id: str) -> None:
        """Clean up transport when connection closes."""
        if session_id in self.transports:
            del self.transports[session_id]
            print(f"Cleaned up transport for session: {session_id}")

    async def start_server(self, host: str = "localhost", port: int = 3001) -> None:
        """Start the HTTP server with SSE support."""
        app = web.Application()
        
        # Add routes
        app.router.get("/sse", self.handle_sse)
        app.router.post("/message", self.handle_message)
        
        # Add health check endpoint
        app.router.get("/health", lambda _: web.json_response({"status": "healthy"}))

        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        print(f"Fetch SSE server running on http://{host}:{port}")
        print("SSE endpoint: GET /sse")
        print("Message endpoint: POST /message")
        print("Health check: GET /health")
        
        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            print("\nShutting down server...")
            await runner.cleanup()


async def main():
    """Main entry point for the HTTP SSE server."""
    import argparse

    parser = argparse.ArgumentParser(
        description="MCP Fetch Server with HTTP+SSE transport"
    )
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=3001, help="Port to bind to")
    parser.add_argument("--user-agent", type=str, help="Custom User-Agent string")
    parser.add_argument(
        "--ignore-robots-txt",
        action="store_true",
        help="Ignore robots.txt restrictions",
    )
    parser.add_argument("--proxy-url", type=str, help="Proxy URL to use for requests")

    args = parser.parse_args()

    server = FetchSSEServer(
        custom_user_agent=args.user_agent,
        ignore_robots_txt=args.ignore_robots_txt,
        proxy_url=args.proxy_url,
    )

    await server.start_server(args.host, args.port)


if __name__ == "__main__":
    asyncio.run(main()) 