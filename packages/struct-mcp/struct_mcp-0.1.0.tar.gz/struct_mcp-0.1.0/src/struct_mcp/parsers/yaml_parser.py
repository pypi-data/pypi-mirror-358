"""
YAML parser for structure definitions.
"""

from pathlib import Path
from typing import Any, Dict, Union
import yaml


class YAMLParser:
    """Parser for YAML structure definition files."""

    def parse(self, yaml_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse a YAML structure definition file."""
        yaml_path = Path(yaml_path)

        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")

        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                raise ValueError(
                    "YAML file must contain a dictionary at the root level"
                )

            return data

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing YAML file: {e}")

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate the structure of parsed YAML data."""
        # Basic validation - can be extended
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
