"""Configuration management for Fast Clean Architecture."""

from pathlib import Path
from typing import Dict, List, Optional, Union

import re
import yaml
from pydantic import BaseModel, Field

from .exceptions import ConfigurationError, ValidationError
from .utils import generate_timestamp


class ComponentInfo(BaseModel):
    """Information about a component."""

    name: str
    file_path: Optional[str] = None
    created_at: str = Field(default_factory=generate_timestamp)
    updated_at: str = Field(default_factory=generate_timestamp)


class ComponentsConfig(BaseModel):
    """Configuration for component default imports."""

    # Component lists
    entities: List[ComponentInfo] = Field(default_factory=list)
    repositories: List[ComponentInfo] = Field(default_factory=list)
    value_objects: List[ComponentInfo] = Field(default_factory=list)
    services: List[ComponentInfo] = Field(default_factory=list)
    commands: List[ComponentInfo] = Field(default_factory=list)
    queries: List[ComponentInfo] = Field(default_factory=list)
    models: List[ComponentInfo] = Field(default_factory=list)
    external: List[ComponentInfo] = Field(default_factory=list)
    internal: List[ComponentInfo] = Field(default_factory=list)
    api: List[ComponentInfo] = Field(default_factory=list)
    schemas: List[ComponentInfo] = Field(default_factory=list)

    default_imports: Dict[str, List[str]] = Field(
        default={
            "entities": ["dataclasses", "typing", "datetime"],
            "repositories": ["typing"],
            "services": ["typing"],
            "api": ["fastapi", "typing"],
            "schemas": ["pydantic", "typing"],
        }
    )


class NamingConfig(BaseModel):
    """Configuration for naming conventions."""

    snake_case: bool = True
    auto_pluralize: bool = True


class TemplatesConfig(BaseModel):
    """Configuration for custom templates."""

    entity: Optional[str] = None
    repository: Optional[str] = None
    service: Optional[str] = None
    api: Optional[str] = None
    schemas: Optional[str] = None
    command: Optional[str] = None
    query: Optional[str] = None
    model: Optional[str] = None
    external: Optional[str] = None
    value_object: Optional[str] = None


class DomainComponents(BaseModel):
    """Domain layer components."""

    entities: List[ComponentInfo] = Field(default_factory=list)
    repositories: List[ComponentInfo] = Field(default_factory=list)
    value_objects: List[ComponentInfo] = Field(default_factory=list)
    services: List[ComponentInfo] = Field(default_factory=list)


class ApplicationComponents(BaseModel):
    """Application layer components."""

    commands: List[ComponentInfo] = Field(default_factory=list)
    queries: List[ComponentInfo] = Field(default_factory=list)
    services: List[ComponentInfo] = Field(default_factory=list)


class InfrastructureComponents(BaseModel):
    """Infrastructure layer components."""

    repositories: List[ComponentInfo] = Field(default_factory=list)
    external: List[ComponentInfo] = Field(default_factory=list)
    models: List[ComponentInfo] = Field(default_factory=list)


class PresentationComponents(BaseModel):
    """Presentation layer components."""

    api: List[ComponentInfo] = Field(default_factory=list)
    schemas: List[ComponentInfo] = Field(default_factory=list)


class ModuleComponents(BaseModel):
    """Components within a module."""

    domain: ComponentsConfig = Field(default_factory=ComponentsConfig)
    application: ComponentsConfig = Field(default_factory=ComponentsConfig)
    infrastructure: ComponentsConfig = Field(default_factory=ComponentsConfig)
    presentation: ComponentsConfig = Field(default_factory=ComponentsConfig)


class ModuleConfig(BaseModel):
    """Configuration for a module."""

    description: str = ""
    created_at: str = Field(default_factory=generate_timestamp)
    updated_at: str = Field(default_factory=generate_timestamp)
    components: ModuleComponents = Field(default_factory=ModuleComponents)


class SystemConfig(BaseModel):
    """Configuration for a system context."""

    description: str = ""
    created_at: str = Field(default_factory=generate_timestamp)
    updated_at: str = Field(default_factory=generate_timestamp)
    modules: Dict[str, ModuleConfig] = Field(default_factory=dict)


class ProjectConfig(BaseModel):
    """Configuration for the project."""

    name: str = ""
    description: str = ""
    version: str = ""
    base_path: Optional[Path] = None
    created_at: str = Field(default_factory=generate_timestamp)
    updated_at: str = Field(default_factory=generate_timestamp)
    systems: Dict[str, SystemConfig] = Field(default_factory=dict)


class Config(BaseModel):
    """Main configuration model."""

    project: ProjectConfig = Field(default_factory=ProjectConfig)
    templates: TemplatesConfig = Field(default_factory=TemplatesConfig)
    naming: NamingConfig = Field(default_factory=NamingConfig)
    components: ComponentsConfig = Field(default_factory=ComponentsConfig)

    @classmethod
    def load_from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file with enhanced security validation."""
        try:
            if not config_path.exists():
                raise ConfigurationError(f"Configuration file not found: {config_path}")

            # Check file size to prevent DoS attacks
            file_size = config_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                raise ConfigurationError(
                    f"Configuration file too large: {file_size} bytes"
                )

            with open(config_path, "r", encoding="utf-8") as f:
                # Use safe_load for security
                data = yaml.safe_load(f) or {}

            # Validate loaded data structure
            if not isinstance(data, dict):
                raise ConfigurationError(
                    "Configuration file must contain a YAML object/dictionary"
                )

            # Sanitize loaded data before creating config object
            sanitized_data = cls._sanitize_loaded_data(data)

            return cls(**sanitized_data)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading config: {e}")

    @staticmethod
    def _sanitize_loaded_data(data: dict) -> dict:
        """Sanitize data loaded from YAML file to prevent injection attacks.

        Args:
            data: Raw data loaded from YAML file

        Returns:
            Sanitized data safe for Config object creation
        """

        def sanitize_value(value):
            if value is None:
                return None
            elif isinstance(value, bool):
                return value
            elif isinstance(value, (int, float)):
                # Validate numeric ranges
                if isinstance(value, float) and (
                    value != value or abs(value) == float("inf")
                ):
                    return 0.0
                return value
            elif isinstance(value, str):
                # Remove control characters and YAML-specific dangerous patterns
                sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", value)
                sanitized = re.sub(r"^[!&*|>%@`]", "", sanitized)
                # Limit string length
                if len(sanitized) > 10000:
                    sanitized = sanitized[:10000]
                return sanitized
            elif isinstance(value, list):
                return [sanitize_value(item) for item in value]
            elif isinstance(value, dict):
                sanitized_dict = {}
                for k, v in value.items():
                    # Sanitize keys
                    if not isinstance(k, str):
                        k = str(k)
                    sanitized_key = re.sub(
                        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", k
                    )
                    sanitized_key = re.sub(r"^[!&*|>%@`]", "", sanitized_key)
                    if len(sanitized_key) > 1000:
                        sanitized_key = sanitized_key[:1000]
                    if sanitized_key:  # Skip empty keys
                        sanitized_dict[sanitized_key] = sanitize_value(v)
                return sanitized_dict
            else:
                # Convert unknown types to string and sanitize
                return sanitize_value(str(value))

        return sanitize_value(data)

    @classmethod
    def create_default(cls) -> "Config":
        """Create default configuration without saving to file."""
        timestamp = generate_timestamp()

        return cls(
            project=ProjectConfig(
                name="my_project",
                description="My FastAPI project",
                version="0.1.0",
                created_at=timestamp,
                updated_at=timestamp,
            )
        )

    @classmethod
    def create_default_config(cls, config_path: Path) -> "Config":
        """Create default configuration."""
        timestamp = generate_timestamp()
        project_name = config_path.parent.name

        config = cls(
            project=ProjectConfig(
                name=project_name,
                created_at=timestamp,
                updated_at=timestamp,
            )
        )

        config.save_to_file(config_path)
        return config

    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to YAML file with atomic write and backup."""
        import tempfile
        from datetime import datetime

        backup_path = None
        temp_path = None

        try:
            # Create timestamped backup if file exists
            if config_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = config_path.with_suffix(f".yaml.backup.{timestamp}")
                backup_path.write_bytes(config_path.read_bytes())

                # Clean up old backups (keep only last 5)
                self._cleanup_old_backups(config_path)

            # Ensure parent directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temporary file first (atomic write)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=config_path.parent,
                delete=False,
                suffix=".tmp",
            ) as f:
                temp_path = Path(f.name)
                # Sanitize configuration data before dumping
                raw_data = self.model_dump(exclude_none=True)
                config_data = self._sanitize_config_data(raw_data)

                # Ensure we have a dict for YAML serialization
                if not isinstance(config_data, dict):
                    raise ConfigurationError(
                        "Sanitized configuration data must be a dictionary"
                    )

                # Use safe_dump for security
                yaml.safe_dump(
                    config_data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=2,
                    allow_unicode=True,
                )

            # Atomic move
            temp_path.replace(config_path)

        except Exception as e:
            # Clean up temporary file on error
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass

            # Restore from backup if available
            if backup_path and backup_path.exists() and not config_path.exists():
                try:
                    backup_path.rename(config_path)
                except:
                    pass

            raise ConfigurationError(f"Error saving config: {e}")

    def _sanitize_config_data(
        self, data: Union[dict, list, str, int, float, bool, None]
    ) -> Union[dict, list, str, int, float, bool, None]:
        """Sanitize configuration data to prevent injection attacks and ensure safe YAML output.

        Args:
            data: The configuration data to sanitize

        Returns:
            Sanitized configuration data safe for YAML serialization
        """
        if data is None:
            return None
        elif isinstance(data, bool):
            return data
        elif isinstance(data, (int, float)):
            # Validate numeric ranges to prevent potential issues
            if isinstance(data, float) and (data != data or abs(data) == float("inf")):
                return 0.0  # Replace NaN and infinity with safe default
            return data
        elif isinstance(data, str):
            # Remove potentially dangerous characters and control sequences
            sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", data)
            # Remove YAML-specific dangerous patterns
            sanitized = re.sub(r"^[!&*|>%@`]", "", sanitized)
            # Limit string length to prevent DoS
            if len(sanitized) > 10000:
                sanitized = sanitized[:10000]
            return sanitized
        elif isinstance(data, list):
            # Recursively sanitize list items
            return [self._sanitize_config_data(item) for item in data]
        elif isinstance(data, dict):
            # Recursively sanitize dictionary values and validate keys
            sanitized_dict = {}
            for key, value in data.items():
                # Sanitize keys (must be strings for YAML)
                if not isinstance(key, str):
                    key = str(key)
                # Remove dangerous characters from keys
                sanitized_key = re.sub(
                    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", key
                )
                sanitized_key = re.sub(r"^[!&*|>%@`]", "", sanitized_key)
                if len(sanitized_key) > 1000:
                    sanitized_key = sanitized_key[:1000]

                # Skip empty keys
                if not sanitized_key:
                    continue

                sanitized_dict[sanitized_key] = self._sanitize_config_data(value)
            return sanitized_dict
        else:
            # Convert unknown types to string and sanitize
            return self._sanitize_config_data(str(data))

    def _cleanup_old_backups(self, config_path: Path, keep_count: int = 5) -> None:
        """Clean up old backup files, keeping only the most recent ones."""
        try:
            backup_pattern = f"{config_path.name}.backup.*"
            backup_files = list(config_path.parent.glob(backup_pattern))

            if len(backup_files) > keep_count:
                # Sort by modification time (newest first)
                backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

                # Remove old backups
                for old_backup in backup_files[keep_count:]:
                    try:
                        old_backup.unlink()
                    except OSError:
                        # Ignore errors when cleaning up old backups
                        pass
        except Exception:
            # Don't fail the main operation if backup cleanup fails
            pass

    def add_system(self, system_name: str, description: str = "") -> None:
        """Add a new system context."""
        if system_name in self.project.systems:
            raise ValidationError(f"System '{system_name}' already exists")

        timestamp = generate_timestamp()

        self.project.systems[system_name] = SystemConfig(
            description=description,
            created_at=timestamp,
            updated_at=timestamp,
        )
        self.project.updated_at = timestamp

    def add_module(
        self, system_name: str, module_name: str, description: str = ""
    ) -> None:
        """Add a new module to a system."""
        if system_name not in self.project.systems:
            raise ValidationError(f"System '{system_name}' not found")

        if module_name in self.project.systems[system_name].modules:
            raise ValidationError(f"Module '{module_name}' already exists")

        timestamp = generate_timestamp()

        self.project.systems[system_name].modules[module_name] = ModuleConfig(
            description=description,
            created_at=timestamp,
            updated_at=timestamp,
        )
        self.project.systems[system_name].updated_at = timestamp
        self.project.updated_at = timestamp

    def add_component(
        self,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
        file_path: Optional[str] = None,
    ) -> None:
        """Add a component to a module."""
        if system_name not in self.project.systems:
            raise ConfigurationError(f"System '{system_name}' does not exist")

        if module_name not in self.project.systems[system_name].modules:
            raise ValidationError(f"Module '{module_name}' not found")

        # Validate layer
        valid_layers = ["domain", "application", "infrastructure", "presentation"]
        if layer not in valid_layers:
            raise ValidationError(f"Invalid layer: {layer}")

        timestamp = generate_timestamp()
        module = self.project.systems[system_name].modules[module_name]

        # Get the layer components
        layer_components = getattr(module.components, layer)

        # Validate component type for the layer
        if not hasattr(layer_components, component_type):
            raise ValidationError(f"Invalid component type: {component_type}")

        # Get the specific component type list
        component_list = getattr(layer_components, component_type)

        # Check if component already exists
        existing_component = next(
            (comp for comp in component_list if comp.name == component_name), None
        )

        if existing_component is None:
            # Create new component
            component_info = ComponentInfo(
                name=component_name,
                file_path=file_path,
                created_at=timestamp,
                updated_at=timestamp,
            )
            component_list.append(component_info)
            # Sort by name to keep alphabetical order
            component_list.sort(key=lambda x: x.name)

        # Update timestamps
        module.updated_at = timestamp
        self.project.systems[system_name].updated_at = timestamp
        self.project.updated_at = timestamp
