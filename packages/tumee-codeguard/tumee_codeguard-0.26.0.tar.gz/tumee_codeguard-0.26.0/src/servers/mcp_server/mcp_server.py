"""FastMCP server instance - separated to avoid circular imports."""

from fastmcp import FastMCP

# Create the FastMCP server instance
mcp = FastMCP("CodeGuard")


def register_tools():
    """Register all MCP tools. Call this only when starting the MCP server."""
    # Import all tool modules to trigger @mcp.tool() decorator registration
    from .tools import codeguard_unified  # Registers: codeguard
    from .tools.smart import main as smart_main  # Registers: smart
