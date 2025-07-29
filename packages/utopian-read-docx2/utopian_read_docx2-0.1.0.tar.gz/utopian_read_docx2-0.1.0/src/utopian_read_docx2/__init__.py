# server.py
from mcp.server.fastmcp import FastMCP
import docx2txt

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def read_docx(path: str) -> str:
    """读取docx文件内容"""
    text = docx2txt.process(path)
    return text

# # Add an addition tool
# @mcp.tool()
# def add(a: int, b: int) -> int:
#     """Add two numbers"""
#     return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


def main() -> None:
    mcp.run(transport='stdio')
