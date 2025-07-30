"""
MCP server implementation for struct-mcp.
"""

import asyncio
from typing import Any, Dict, Optional
from urllib.parse import urlparse
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities

from .struct_parser import StructMCP


def extract_structure_name_from_uri(uri: str) -> str:
    """
    Extract structure name from a URI of any scheme.

    Args:
        uri: URI string (can be AnyUrl object, gets converted to string)

    Returns:
        str: The extracted structure name

    Raises:
        ValueError: If structure name cannot be extracted from URI

    Examples:
        >>> extract_structure_name_from_uri("struct://cheese_inventory")
        'cheese_inventory'
        >>> extract_structure_name_from_uri("https://example.com/api/cheese_inventory")
        'cheese_inventory'
        >>> extract_structure_name_from_uri("file:///path/to/cheese_inventory")
        'cheese_inventory'
    """
    uri_str = str(uri)  # Convert AnyUrl to string
    parsed = urlparse(uri_str)

    # Try to extract structure name from various URI parts
    # Priority: path segments first, then netloc for scheme://name pattern
    structure_name = None

    if parsed.path:
        # Get the last non-empty path segment
        path_parts = [p for p in parsed.path.split("/") if p]
        if path_parts:
            structure_name = path_parts[-1]

    # If no path or empty path, try netloc (for patterns like struct://name)
    if not structure_name and parsed.netloc:
        structure_name = parsed.netloc

    if not structure_name:
        raise ValueError(f"Cannot extract structure name from URI: {uri_str}")

    return structure_name


class MCPServer:
    """MCP server that provides queryable interface for data structures."""

    def __init__(self, struct_mcp: StructMCP):
        self.struct_mcp = struct_mcp
        self.server = Server("struct-mcp")
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up MCP server handlers."""

        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available structure resources."""
            resources = []
            for structure_name in self.struct_mcp.get_structure_names():
                resources.append(
                    Resource(
                        uri=f"struct://{structure_name}",
                        name=f"Structure: {structure_name}",
                        description=f"Data structure definition for {structure_name}",
                        mimeType="application/json",
                    )
                )
            return resources

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a structure resource."""
            structure_name = extract_structure_name_from_uri(uri)

            structure = self.struct_mcp.get_structure(structure_name)
            if structure:
                import json

                return json.dumps(structure, indent=2)
            else:
                raise ValueError(f"Structure '{structure_name}' not found")

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="query_structure",
                    description="Query data structure with natural language questions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "Natural language question about the data structure",
                            },
                            "structure_name": {
                                "type": "string",
                                "description": "Name of the structure to query (optional if only one structure)",
                            },
                        },
                        "required": ["question"],
                    },
                ),
                Tool(
                    name="get_fields",
                    description="Get all fields for a structure",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "structure_name": {
                                "type": "string",
                                "description": "Name of the structure",
                            }
                        },
                        "required": ["structure_name"],
                    },
                ),
                Tool(
                    name="find_fields_with_property",
                    description="Find fields that have a specific property",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "structure_name": {
                                "type": "string",
                                "description": "Name of the structure",
                            },
                            "property_name": {
                                "type": "string",
                                "description": "Name of the property to search for",
                            },
                            "property_value": {
                                "type": "string",
                                "description": "Optional: specific value of the property",
                            },
                        },
                        "required": ["structure_name", "property_name"],
                    },
                ),
                Tool(
                    name="convert_format",
                    description="Convert structure to different format",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "format": {
                                "type": "string",
                                "enum": ["opensearch", "avro", "pydantic"],
                                "description": "Target format for conversion",
                            }
                        },
                        "required": ["format"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> list[Dict[str, Any]]:
            """Handle tool calls."""
            try:
                if name == "query_structure":
                    question = arguments["question"]
                    structure_name = arguments.get("structure_name")
                    answer = self.struct_mcp.answer_question(question, structure_name)
                    return [{"type": "text", "text": answer}]

                elif name == "get_fields":
                    structure_name = arguments["structure_name"]
                    fields = self.struct_mcp.get_fields(structure_name)
                    import json

                    return [{"type": "text", "text": json.dumps(fields, indent=2)}]

                elif name == "find_fields_with_property":
                    structure_name = arguments["structure_name"]
                    property_name = arguments["property_name"]
                    property_value = arguments.get("property_value")

                    if property_value:
                        fields = self.struct_mcp.find_fields_with_property(
                            structure_name, property_name, property_value
                        )
                    else:
                        fields = self.struct_mcp.find_fields_with_property(
                            structure_name, property_name
                        )

                    import json

                    return [{"type": "text", "text": json.dumps(fields, indent=2)}]

                elif name == "convert_format":
                    format_type = arguments["format"]
                    if format_type == "opensearch":
                        result = self.struct_mcp.to_opensearch()
                    elif format_type == "avro":
                        result = self.struct_mcp.to_avro()
                    elif format_type == "pydantic":
                        result = self.struct_mcp.to_pydantic()
                    else:
                        raise ValueError(f"Unsupported format: {format_type}")

                    return [{"type": "text", "text": result}]

                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                return [{"type": "text", "text": f"Error: {str(e)}"}]

    def start(self):
        """Start the MCP server."""

        async def main():
            try:
                async with stdio_server() as (read_stream, write_stream):
                    await self.server.run(
                        read_stream,
                        write_stream,
                        InitializationOptions(
                            server_name="struct-mcp",
                            server_version="0.1.0",
                            capabilities=ServerCapabilities(
                                resources={}, tools={}, prompts={}
                            ),
                        ),
                    )
            except KeyboardInterrupt:
                pass  # Clean exit on Ctrl+C

        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass  # Clean exit on Ctrl+C
