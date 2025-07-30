# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("mcp-yitu-ai", version="0.1.0", description="MCP server for Yitu AI")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

def main() -> None:
    mcp.run(transport='stdio')
