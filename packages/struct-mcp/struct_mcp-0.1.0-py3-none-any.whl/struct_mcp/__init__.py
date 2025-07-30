"""
Struct-MCP: Transform data structure definitions into queryable MCP servers.
"""

from .struct_parser import StructMCP
from .mcp_server import MCPServer

__version__ = "0.1.0"
__all__ = ["StructMCP", "MCPServer"]
