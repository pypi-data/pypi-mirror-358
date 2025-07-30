"""
Core structure parsing logic for struct-mcp.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml

from .parsers.yaml_parser import YAMLParser
from .parsers.json_schema_parser import JSONSchemaParser
from .parsers.opensearch_parser import OpenSearchParser
from .parsers.avro_parser import AvroParser
from .parsers.pydantic_parser import PydanticParser
from .parsers.protobuf_parser import ProtobufParser


class StructMCP:
    """Main class for parsing and querying data structure definitions."""

    def __init__(self, structures: Dict[str, Any]):
        """Initialize with parsed structure data."""
        self.structures = structures

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "StructMCP":
        """Load structure definition from any supported file format."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine parser based on file extension
        suffix = file_path.suffix.lower()

        if suffix in [".yaml", ".yml"]:
            parser = YAMLParser()
        elif suffix == ".json":
            # Load JSON data first, then detect format
            with open(file_path, "r") as f:
                import json

                data = json.load(f)

            # Check format and use appropriate parser
            if cls._looks_like_opensearch(data):
                parser = OpenSearchParser()
            elif cls._looks_like_avro(data):
                parser = AvroParser()
            else:
                # Default to JSON Schema parser
                parser = JSONSchemaParser()
        elif suffix == ".py":
            parser = PydanticParser()
        elif suffix == ".proto":
            parser = ProtobufParser()
        else:
            raise ValueError(
                f"Unsupported file format: {suffix}. Supported formats: .yaml, .yml, .json, .py, .proto"
            )

        structures = parser.parse(file_path)
        return cls(structures)

    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]) -> "StructMCP":
        """Load structure definition from YAML file."""
        parser = YAMLParser()
        structures = parser.parse(yaml_path)
        return cls(structures)

    @classmethod
    def from_json_schema(cls, schema_path: Union[str, Path]) -> "StructMCP":
        """Load structure definition from JSON Schema file."""
        parser = JSONSchemaParser()
        structures = parser.parse(schema_path)
        return cls(structures)

    @classmethod
    def from_opensearch(cls, mapping_path: Union[str, Path]) -> "StructMCP":
        """Load structure definition from OpenSearch mapping file."""
        parser = OpenSearchParser()
        structures = parser.parse(mapping_path)
        return cls(structures)

    @classmethod
    def from_avro(cls, schema_path: Union[str, Path]) -> "StructMCP":
        """Load structure definition from Avro schema file."""
        parser = AvroParser()
        structures = parser.parse(schema_path)
        return cls(structures)

    @classmethod
    def from_pydantic(cls, model_path: Union[str, Path]) -> "StructMCP":
        """Load structure definition from Pydantic model file."""
        parser = PydanticParser()
        structures = parser.parse(model_path)
        return cls(structures)

    @classmethod
    def from_protobuf(cls, proto_path: Union[str, Path]) -> "StructMCP":
        """Load structure definition from Protocol Buffer file."""
        parser = ProtobufParser()
        structures = parser.parse(proto_path)
        return cls(structures)

    @staticmethod
    def _looks_like_opensearch(data: Dict[str, Any]) -> bool:
        """Check if JSON data looks like OpenSearch mapping format."""
        if not isinstance(data, dict):
            return False

        # Look for OpenSearch mapping patterns
        for value in data.values():
            if isinstance(value, dict):
                if "mappings" in value or "properties" in value:
                    return True
                # Check for direct field type definitions
                if "type" in value and value["type"] in [
                    "text",
                    "keyword",
                    "integer",
                    "double",
                    "boolean",
                    "date",
                ]:
                    return True

        return False

    @staticmethod
    def _looks_like_avro(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> bool:
        """Check if JSON data looks like Avro schema format."""
        if isinstance(data, dict):
            return data.get("type") == "record" and "fields" in data
        elif isinstance(data, list):
            return all(
                isinstance(item, dict) and item.get("type") == "record" for item in data
            )

        return False

    def get_structure_names(self) -> List[str]:
        """Get all structure names."""
        return list(self.structures.keys())

    def get_structure(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific structure by name."""
        return self.structures.get(name)

    def get_fields(self, structure_name: str) -> Dict[str, Any]:
        """Get all fields for a structure."""
        structure = self.get_structure(structure_name)
        if structure and "fields" in structure:
            return structure["fields"]
        return {}

    def get_field(
        self, structure_name: str, field_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific field from a structure."""
        fields = self.get_fields(structure_name)
        return fields.get(field_name)

    def find_fields_with_property(
        self, structure_name: str, property_name: str, property_value: Any = None
    ) -> Dict[str, Any]:
        """Find fields that have a specific property, optionally with a specific value."""
        fields = self.get_fields(structure_name)
        result = {}

        for field_name, field_data in fields.items():
            if isinstance(field_data, dict) and property_name in field_data:
                if (
                    property_value is None
                    or field_data[property_name] == property_value
                ):
                    result[field_name] = field_data

        return result

    def find_fields_by_pattern(
        self, structure_name: str, property_name: str, pattern: str
    ) -> Dict[str, Any]:
        """Find fields where a property contains a pattern."""
        fields = self.get_fields(structure_name)
        result = {}

        for field_name, field_data in fields.items():
            if isinstance(field_data, dict) and property_name in field_data:
                prop_value = field_data[property_name]
                if (
                    isinstance(prop_value, str)
                    and pattern.lower() in prop_value.lower()
                ):
                    result[field_name] = field_data

        return result

    def get_all_property_values(
        self, structure_name: str, property_name: str
    ) -> List[Any]:
        """Get all unique values for a property across all fields."""
        fields = self.get_fields(structure_name)
        values = set()

        for field_data in fields.values():
            if isinstance(field_data, dict) and property_name in field_data:
                values.add(field_data[property_name])

        return sorted(list(values))

    def answer_question(
        self, question: str, structure_name: Optional[str] = None
    ) -> str:
        """Answer natural language questions about the structure(s)."""
        question_lower = question.lower()

        # If no structure specified, try to infer or use the first one
        if not structure_name:
            structure_names = self.get_structure_names()
            if len(structure_names) == 1:
                structure_name = structure_names[0]
            else:
                return f"Multiple structures available: {', '.join(structure_names)}. Please specify which one."

        structure = self.get_structure(structure_name)
        if not structure:
            return f"Structure '{structure_name}' not found."

        # Handle field-specific questions
        if "what does" in question_lower and (
            "represent" in question_lower or "mean" in question_lower
        ):
            # Try to find field name in question
            words = question.split()
            for word in words:
                clean_word = word.strip("?.,")
                field = self.get_field(structure_name, clean_word)
                if field:
                    parts = []
                    if isinstance(field, dict):
                        for key, value in field.items():
                            if key != "type" and isinstance(value, str):
                                parts.append(f"{key}: {value}")
                    return (
                        f"{clean_word} - " + "; ".join(parts)
                        if parts
                        else f"{clean_word} is defined in the structure"
                    )

        # Handle property-based questions
        for prop in ["type", "nullable", "repeated", "description"]:
            if prop in question_lower:
                fields_with_prop = self.find_fields_with_property(structure_name, prop)
                if fields_with_prop:
                    field_names = list(fields_with_prop.keys())
                    return f"Fields with {prop}: {', '.join(field_names)}"

        return f"I'm not sure how to answer that question about {structure_name}."

    def to_opensearch(self) -> str:
        """Convert structure to OpenSearch mapping format."""
        from .converters.opensearch import OpenSearchConverter

        converter = OpenSearchConverter()
        return converter.convert(self.structures)

    def to_avro(self) -> str:
        """Convert structure to Avro schema format."""
        from .converters.avro import AvroConverter

        converter = AvroConverter()
        return converter.convert(self.structures)

    def to_pydantic(self) -> str:
        """Convert structure to Pydantic model format."""
        from .converters.pydantic import PydanticConverter

        converter = PydanticConverter()
        return converter.convert(self.structures)

    def to_protobuf(self) -> str:
        """Convert structure to Protocol Buffer schema format."""
        from .converters.protobuf import ProtobufConverter

        converter = ProtobufConverter()
        return converter.convert(self.structures)

    def generate_docs(self) -> str:
        """Generate markdown documentation for the structure(s)."""
        lines = []

        for structure_name, structure_data in self.structures.items():
            lines.append(f"# {structure_name}")
            lines.append("")

            # Add any top-level properties as metadata
            if isinstance(structure_data, dict):
                metadata = {k: v for k, v in structure_data.items() if k != "fields"}
                if metadata:
                    lines.append("## Metadata")
                    lines.append("")
                    for key, value in metadata.items():
                        lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
                    lines.append("")

                # Add fields
                if "fields" in structure_data:
                    lines.append("## Fields")
                    lines.append("")

                    for field_name, field_data in structure_data["fields"].items():
                        lines.append(f"### {field_name}")
                        lines.append("")

                        if isinstance(field_data, dict):
                            for prop_name, prop_value in field_data.items():
                                lines.append(
                                    f"- **{prop_name.replace('_', ' ').title()}**: {prop_value}"
                                )
                        else:
                            lines.append(f"- **Value**: {field_data}")

                        lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)
