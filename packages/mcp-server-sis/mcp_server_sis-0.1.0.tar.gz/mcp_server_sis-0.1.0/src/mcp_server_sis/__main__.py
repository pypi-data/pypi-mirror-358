import argparse
import os
from .sis import mcp

def main():
    parser = argparse.ArgumentParser(description="Start MCP SIS server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default= 3000, help="Port to listen on (default: 3000)")
    parser.add_argument("--transport", type=str, default= "sse", help="Transport type (default: sse)")
    args = parser.parse_args()

    mcp.run(transport=args.transport, host=args.host, port=args.port)

if __name__ == "__main__":
    main()