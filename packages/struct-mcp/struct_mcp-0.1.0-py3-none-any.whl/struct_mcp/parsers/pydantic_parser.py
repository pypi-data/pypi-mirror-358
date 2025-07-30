"""
Pydantic model parser for structure definitions.
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class PydanticParser:
    """Parser for Pydantic model files."""

    def parse(self, model_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse a Pydantic model file."""
        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(f"Pydantic model file not found: {model_path}")

        try:
            with open(model_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the Python AST
            tree = ast.parse(content)

            # Convert Pydantic models to our internal format
            return self._convert_pydantic_models(tree, content)

        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing Pydantic model file: {e}")

    def _convert_pydantic_models(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Convert Pydantic models from AST to our internal structure format."""
        result = {}

        # Find all class definitions that inherit from BaseModel
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from BaseModel
                if self._inherits_from_basemodel(node):
                    class_name = node.name
                    structure_name = self._to_structure_name(class_name)
                    result[structure_name] = self._convert_pydantic_class(node, content)

        return result

    def _inherits_from_basemodel(self, class_node: ast.ClassDef) -> bool:
        """Check if a class inherits from BaseModel."""
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                # Direct inheritance from BaseModel or aliased BaseModel (BM, etc)
                if base.id == "BaseModel" or base.id == "BM":
                    return True
            elif isinstance(base, ast.Attribute) and base.attr == "BaseModel":
                return True
        return False

    def _convert_pydantic_class(
        self, class_node: ast.ClassDef, content: str
    ) -> Dict[str, Any]:
        """Convert a Pydantic class to our internal format."""
        result = {}

        # Extract docstring as description
        docstring = ast.get_docstring(class_node)
        if docstring:
            result["description"] = docstring.strip()
        else:
            result["description"] = (
                f"Structure imported from Pydantic model: {class_node.name}"
            )

        # Convert fields
        result["fields"] = {}

        # Find field annotations
        for node in class_node.body:
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                field_name = node.target.id
                field_info = self._parse_field_annotation(node, content)
                result["fields"][field_name] = field_info

        return result

    def _parse_field_annotation(
        self, ann_assign: ast.AnnAssign, content: str
    ) -> Dict[str, Any]:
        """Parse a field annotation to extract type and metadata."""
        result = {
            "nullable": False,
            "repeated": False,
            "description": "Field imported from Pydantic model",
        }

        # Parse the type annotation
        annotation = ann_assign.annotation
        type_info = self._parse_type_annotation(annotation)
        result.update(type_info)

        # Check for Field() definition to extract description
        if ann_assign.value:
            field_description = self._extract_field_description(
                ann_assign.value, content
            )
            if field_description:
                result["description"] = field_description

        # Check for default value (indicates nullable)
        if ann_assign.value:
            if (
                isinstance(ann_assign.value, ast.Constant)
                and ann_assign.value.value is None
            ):
                result["nullable"] = True

        return result

    def _parse_type_annotation(self, annotation: ast.AST) -> Dict[str, Any]:
        """Parse type annotation and return type information."""
        result = {"type": "string"}

        if isinstance(annotation, ast.Name):
            # Simple types like str, int, bool
            result["type"] = self._map_python_type(annotation.id)

        elif isinstance(annotation, ast.Subscript):
            # Generic types like List[str], Optional[int]
            if isinstance(annotation.value, ast.Name):
                container_type = annotation.value.id

                if container_type == "List":
                    result["repeated"] = True
                    # Extract item type
                    if isinstance(annotation.slice, ast.Name):
                        result["type"] = self._map_python_type(annotation.slice.id)
                    else:
                        result["type"] = "string"

                elif container_type == "Optional":
                    result["nullable"] = True
                    # Extract base type
                    if isinstance(annotation.slice, ast.Name):
                        result["type"] = self._map_python_type(annotation.slice.id)
                    elif isinstance(annotation.slice, ast.Subscript):
                        # Handle Optional[List[str]]
                        inner_info = self._parse_type_annotation(annotation.slice)
                        result.update(inner_info)
                    else:
                        result["type"] = "string"

        elif isinstance(annotation, ast.Constant):
            # Handle string type annotations
            if isinstance(annotation.value, str):
                result["type"] = self._map_python_type(annotation.value)

        return result

    def _extract_field_description(
        self, value_node: ast.AST, content: str
    ) -> Optional[str]:
        """Extract description from Field() call."""
        if isinstance(value_node, ast.Call):
            if isinstance(value_node.func, ast.Name) and value_node.func.id == "Field":
                # Look for description keyword argument
                for keyword in value_node.keywords:
                    if keyword.arg == "description":
                        if isinstance(keyword.value, ast.Constant):
                            return keyword.value.value
        return None

    def _map_python_type(self, python_type: str) -> str:
        """Map Python types to our internal types."""
        type_mapping = {
            "str": "string",
            "int": "integer",
            "bool": "boolean",
            "float": "decimal",
            "bytes": "string",
            "datetime": "string",
            "date": "string",
        }

        return type_mapping.get(python_type, "string")

    def _to_structure_name(self, class_name: str) -> str:
        """Convert PascalCase class name to snake_case structure name."""
        # Convert PascalCase to snake_case, handling consecutive uppercase letters
        # XMLHttpRequest -> xmlhttp_request, IODevice -> iodevice
        # First, handle the sequence: lowercase/digit followed by uppercase
        s1 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", class_name)
        # Then handle: uppercase followed by uppercase+lowercase (but keep consecutive uppers together)
        s2 = re.sub("([A-Z])([A-Z][a-z])", r"\1\2", s1)
        return s2.lower()

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate the structure of parsed Pydantic model data."""
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

        return True
