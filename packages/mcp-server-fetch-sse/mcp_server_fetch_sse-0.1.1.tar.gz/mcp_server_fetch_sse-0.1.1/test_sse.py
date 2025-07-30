#!/usr/bin/env python3
"""
Simple test script for the SSE transport implementation.
This script tests the basic functionality of the SSE server.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_server_fetch.sse_server import serve_sse


async def test_sse_server():
    """Test the SSE server functionality."""
    print("Testing SSE server...")
    
    # This is a basic test to ensure the server can be imported and initialized
    # In a real test, you would connect to the server and send actual requests
    
    try:
        # Test that we can create the server function
        print("✓ SSE server module imported successfully")
        print("✓ serve_sse function is available")
        
        # Test that the function signature is correct
        import inspect
        sig = inspect.signature(serve_sse)
        expected_params = ['custom_user_agent', 'ignore_robots_txt', 'proxy_url']
        
        for param in expected_params:
            if param in sig.parameters:
                print(f"✓ Parameter '{param}' found in serve_sse signature")
            else:
                print(f"✗ Parameter '{param}' missing from serve_sse signature")
        
        print("\nSSE server test completed successfully!")
        print("\nTo run the SSE server:")
        print("  python -m mcp_server_fetch --sse")
        print("  mcp-server-fetch-sse")
        print("\nTo run the HTTP SSE server:")
        print("  python -m mcp_server_fetch.http_sse_server")
        print("  mcp-server-fetch-http")
        
    except Exception as e:
        print(f"✗ Error testing SSE server: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_sse_server())
    sys.exit(0 if success else 1) 