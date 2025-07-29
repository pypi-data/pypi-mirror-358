import argparse
from .weathermcpqhzy import mcp

def main() -> None:
    """Start an MCP server using the provided FastMCP instance."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="Transport to use for the MCP server.",
    )
    parser.add_argument("--port", type=int, default=8000, help="Port to serve on.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to.")

    args = parser.parse_args()

    if args.transport == "streamable-http":
        mcp.run(
            transport="streamable-http",
            port=args.port,
            host=args.host,
        )
    else:
        mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

