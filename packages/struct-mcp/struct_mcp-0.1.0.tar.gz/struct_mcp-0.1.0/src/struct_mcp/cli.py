"""
Command-line interface for struct-mcp.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .struct_parser import StructMCP
from .mcp_server import MCPServer


def serve_command(args: argparse.Namespace) -> None:
    """Start MCP server with a structure definition file."""
    input_file = Path(args.input_file)
    if not input_file.exists():
        print(f"Error: File {input_file} does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        struct_mcp = StructMCP.from_file(input_file)
        server = MCPServer(struct_mcp)
        server.start()
    except Exception as e:
        import traceback

        print(f"Error starting server: {e}", file=sys.stderr)
        print(f"Full traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


def validate_command(args: argparse.Namespace) -> None:
    """Validate a structure definition file."""
    input_file = Path(args.input_file)
    if not input_file.exists():
        print(f"Error: File {input_file} does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        StructMCP.from_file(input_file)
        print(f"✓ {input_file} is valid")
    except Exception as e:
        print(f"✗ {input_file} is invalid: {e}", file=sys.stderr)
        sys.exit(1)


def convert_command(args: argparse.Namespace) -> None:
    """Convert structure definition to other formats."""
    input_file = Path(args.input_file)
    if not input_file.exists():
        print(f"Error: File {input_file} does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        struct_mcp = StructMCP.from_file(input_file)

        if args.to == "opensearch":
            result = struct_mcp.to_opensearch()
        elif args.to == "avro":
            result = struct_mcp.to_avro()
        elif args.to == "pydantic":
            result = struct_mcp.to_pydantic()
        elif args.to == "protobuf":
            result = struct_mcp.to_protobuf()
        else:
            print(f"Error: Unsupported format '{args.to}'", file=sys.stderr)
            sys.exit(1)

        if args.output:
            with open(args.output, "w") as f:
                f.write(result)
            print(f"Converted to {args.to} format and saved to {args.output}")
        else:
            print(result)

    except Exception as e:
        print(f"Error converting file: {e}", file=sys.stderr)
        sys.exit(1)


def docs_command(args: argparse.Namespace) -> None:
    """Generate documentation for structure definition."""
    input_file = Path(args.input_file)
    if not input_file.exists():
        print(f"Error: File {input_file} does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        struct_mcp = StructMCP.from_file(input_file)
        docs = struct_mcp.generate_docs()

        if args.output:
            with open(args.output, "w") as f:
                f.write(docs)
            print(f"Documentation saved to {args.output}")
        else:
            print(docs)

    except Exception as e:
        print(f"Error generating documentation: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Transform data structure definitions into queryable MCP servers"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start MCP server")
    serve_parser.add_argument(
        "input_file",
        help="Path to structure definition file (YAML, JSON Schema, OpenSearch, Avro, Pydantic, or Protobuf)",
    )
    serve_parser.set_defaults(func=serve_command)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate structure definition"
    )
    validate_parser.add_argument(
        "input_file",
        help="Path to structure definition file (YAML, JSON Schema, OpenSearch, Avro, Pydantic, or Protobuf)",
    )
    validate_parser.set_defaults(func=validate_command)

    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert to other formats")
    convert_parser.add_argument(
        "input_file",
        help="Path to structure definition file (YAML, JSON Schema, OpenSearch, Avro, Pydantic, or Protobuf)",
    )
    convert_parser.add_argument(
        "--to",
        required=True,
        choices=["opensearch", "avro", "pydantic", "protobuf"],
        help="Target format",
    )
    convert_parser.add_argument("--output", help="Output file (default: stdout)")
    convert_parser.set_defaults(func=convert_command)

    # Docs command
    docs_parser = subparsers.add_parser("docs", help="Generate documentation")
    docs_parser.add_argument(
        "input_file",
        help="Path to structure definition file (YAML, JSON Schema, OpenSearch, Avro, Pydantic, or Protobuf)",
    )
    docs_parser.add_argument("--output", help="Output file (default: stdout)")
    docs_parser.set_defaults(func=docs_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
