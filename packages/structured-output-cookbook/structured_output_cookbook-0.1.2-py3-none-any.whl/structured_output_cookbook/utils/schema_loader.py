"""YAML schema loader for custom extraction schemas."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .logger import get_logger


@dataclass
class YamlSchema:
    """Represents a YAML schema configuration."""

    name: str
    description: str
    system_prompt: str
    schema: dict[str, Any]
    filename: str


class SchemaLoader:
    """Loads and manages YAML schemas from the config directory."""

    def __init__(self, config_dir: str = "config/schemas"):
        """Initialize the schema loader.

        Args:
            config_dir: Directory containing YAML schema files
        """
        self.config_dir = Path(config_dir)
        self.logger = get_logger(__name__)

    def get_available_schemas(self) -> list[str]:
        """Get list of available schema names (without .yaml extension).

        Returns:
            List of schema names
        """
        if not self.config_dir.exists():
            return []

        yaml_files = list(self.config_dir.glob("*.yaml")) + list(
            self.config_dir.glob("*.yml"),
        )
        return [f.stem for f in yaml_files]

    def list_schemas_with_descriptions(self) -> list[tuple[str, str]]:
        """Get list of available schemas with their descriptions.

        Returns:
            List of tuples (schema_name, description)
        """
        schemas = []
        for schema_name in self.get_available_schemas():
            try:
                schema = self.load_schema(schema_name)
                schemas.append((schema_name, schema.description))
            except Exception as e:
                self.logger.warning(f"Failed to load schema {schema_name}: {e}")
                schemas.append((schema_name, "Failed to load schema"))

        return schemas

    def load_schema(self, schema_name: str) -> YamlSchema:
        """Load a YAML schema by name.

        Args:
            schema_name: Name of the schema (without .yaml extension)

        Returns:
            YamlSchema object

        Raises:
            FileNotFoundError: If schema file doesn't exist
            yaml.YAMLError: If YAML is invalid
            KeyError: If required fields are missing
        """
        # Try both .yaml and .yml extensions
        schema_paths = [
            self.config_dir / f"{schema_name}.yaml",
            self.config_dir / f"{schema_name}.yml",
        ]

        schema_path = None
        for path in schema_paths:
            if path.exists():
                schema_path = path
                break

        if not schema_path:
            raise FileNotFoundError(
                f"Schema '{schema_name}' not found in {self.config_dir}",
            )

        try:
            with open(schema_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Validate required fields
            required_fields = ["name", "description", "system_prompt", "schema"]
            for field in required_fields:
                if field not in data:
                    raise KeyError(
                        f"Required field '{field}' missing from schema {schema_name}",
                    )

            self.logger.info(f"Loaded schema: {schema_name}")

            return YamlSchema(
                name=data["name"],
                description=data["description"],
                system_prompt=data["system_prompt"],
                schema=data["schema"],
                filename=schema_path.name,
            )

        except yaml.YAMLError as e:
            self.logger.error(f"Invalid YAML in schema {schema_name}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading schema {schema_name}: {e}")
            raise

    def validate_schema_structure(self, schema_name: str) -> tuple[bool, str | None]:
        """Validate that a schema has the correct structure.

        Args:
            schema_name: Name of the schema to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            schema = self.load_schema(schema_name)

            # Check that schema is a dict with type: object
            if not isinstance(schema.schema, dict):
                return False, "Schema must be a dictionary"

            if schema.schema.get("type") != "object":
                return False, "Schema type must be 'object'"

            if "properties" not in schema.schema:
                return False, "Schema must have 'properties' field"

            return True, None

        except Exception as e:
            return False, str(e)
