"""
Protobuf schema parser for structure definitions.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Union


class ProtobufParser:
    """Parser for Protocol Buffer (.proto) files."""

    def parse(self, proto_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse a Protocol Buffer schema file."""
        proto_path = Path(proto_path)

        if not proto_path.exists():
            raise FileNotFoundError(f"Protobuf file not found: {proto_path}")

        try:
            with open(proto_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the proto file content
            return self._parse_proto_content(content)

        except Exception as e:
            raise ValueError(f"Error parsing Protobuf file: {e}")

    def _parse_proto_content(self, content: str) -> Dict[str, Any]:
        """Parse the content of a .proto file."""
        result = {}

        # Remove comments and normalize whitespace
        content = self._preprocess_content(content)

        # Find all message definitions
        messages = self._extract_messages(content)

        for message_name, message_content in messages.items():
            result[message_name] = self._parse_message(message_content, message_name)

        return result

    def _preprocess_content(self, content: str) -> str:
        """Remove comments and normalize the proto file content."""
        # Remove single-line comments
        content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)

        # Remove multi-line comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

        # Normalize whitespace
        content = re.sub(r"\s+", " ", content)

        return content.strip()

    def _extract_messages(self, content: str) -> Dict[str, str]:
        """Extract message definitions from proto content."""
        messages = {}

        # Pattern to match message definitions
        pattern = r"message\s+(\w+)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}"

        matches = re.finditer(pattern, content)
        for match in matches:
            message_name = match.group(1)
            message_body = match.group(2)
            messages[message_name] = message_body

        return messages

    def _parse_message(self, message_content: str, message_name: str) -> Dict[str, Any]:
        """Parse a single message definition."""
        result = {"description": f"Protobuf message: {message_name}", "fields": {}}

        # Extract fields from the message
        fields = self._extract_fields(message_content)

        for field_info in fields:
            field_name = field_info["name"]
            result["fields"][field_name] = {
                "type": field_info["type"],
                "nullable": field_info["nullable"],
                "repeated": field_info["repeated"],
                "description": field_info.get(
                    "description", f"Field {field_name} of type {field_info['type']}"
                ),
            }

        return result

    def _extract_fields(self, message_content: str) -> List[Dict[str, Any]]:
        """Extract field definitions from a message."""
        fields = []

        # Pattern to match field definitions
        # Format: [repeated] [optional] type name = number [options];
        pattern = r"(?:(repeated|optional)\s+)?(\w+)\s+(\w+)\s*=\s*\d+[^;]*;"

        matches = re.finditer(pattern, message_content)
        for match in matches:
            modifier = match.group(1)
            field_type = match.group(2)
            field_name = match.group(3)

            # Skip if this looks like a nested message or enum
            if field_type in ["message", "enum", "service", "rpc"]:
                continue

            field_info = {
                "name": field_name,
                "type": self._map_proto_type(field_type),
                "nullable": modifier == "optional",
                "repeated": modifier == "repeated",
            }

            fields.append(field_info)

        return fields

    def _map_proto_type(self, proto_type: str) -> str:
        """Map Protocol Buffer types to our internal types."""
        type_mapping = {
            # Numeric types
            "double": "decimal",
            "float": "decimal",
            "int32": "integer",
            "int64": "integer",
            "uint32": "integer",
            "uint64": "integer",
            "sint32": "integer",
            "sint64": "integer",
            "fixed32": "integer",
            "fixed64": "integer",
            "sfixed32": "integer",
            "sfixed64": "integer",
            # Boolean
            "bool": "boolean",
            # String and bytes
            "string": "string",
            "bytes": "string",
            # Well-known types
            "google.protobuf.Timestamp": "string",
            "google.protobuf.Duration": "string",
            "google.protobuf.Any": "string",
            "google.protobuf.Empty": "string",
        }

        return type_mapping.get(proto_type, "string")

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate the structure of parsed Protocol Buffer data."""
        if not isinstance(data, dict):
            return False

        # Check that each top-level item has some structure
        for structure_name, structure_data in data.items():
            if not isinstance(structure_data, dict):
                continue

            # If it has fields, validate field structure
            if "fields" in structure_data:
                fields = structure_data["fields"]
                if not isinstance(fields, dict):
                    return False

                # Validate each field has required properties
                for field_name, field_data in fields.items():
                    if not isinstance(field_data, dict):
                        return False

                    required_keys = ["type", "nullable", "repeated"]
                    if not all(key in field_data for key in required_keys):
                        return False

        return True
