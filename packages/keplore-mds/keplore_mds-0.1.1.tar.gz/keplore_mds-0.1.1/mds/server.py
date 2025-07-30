"""MCP Server configuration and setup."""

from mcp.server.fastmcp import FastMCP
from .tools import add, download_dataset, download_model


def create_server() -> FastMCP:
    """Create and configure the MCP server.
    
    Returns:
        Configured FastMCP server instance
    """
    mcp = FastMCP(name="add", version="1.0.0")

    # Register tools with basic parameter descriptions
    mcp.tool(description="Add two numbers")(add)
    mcp.tool(description="Download a dataset from various providers")(download_dataset)
    mcp.tool(description="Download a pretrained model from various providers")(download_model)

    return mcp


def run_server():
    """Run the MCP server with stdio transport."""
    server = create_server()
    print("Starting MCP server...")
    server.run(transport="stdio") 