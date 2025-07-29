"""Configuration updater for managing fca_config.yaml updates."""

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich.console import Console

from ..config import Config
from ..exceptions import ConfigurationError, Result, SecurityError, ValidationError
from ..utils import generate_timestamp
from ..validation import Validator


class ConfigUpdater:
    """Handles updates to the fca_config.yaml file with proper timestamp management."""

    def __init__(self, config_path: Path, console: Optional[Console] = None):
        self.config_path = config_path
        self.console = console or Console()
        self._config: Optional[Config] = None

    @property
    def config(self) -> Config:
        """Lazy load the configuration."""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _load_config(self) -> Config:
        """Load configuration from file or create default."""
        result = self._load_config_safe()
        return result.unwrap()

    def _load_config_safe(self) -> Result[Config, ConfigurationError]:
        """Safely load configuration with Result pattern."""
        try:
            if self.config_path.exists():
                config = Config.load_from_file(self.config_path)
                return Result.success(config)
            else:
                # Create default config if it doesn't exist
                config = Config.create_default()
                config.save_to_file(self.config_path)
                return Result.success(config)
        except Exception as e:
            return Result.failure(
                ConfigurationError(
                    f"Failed to load configuration from {self.config_path}",
                    context={"path": str(self.config_path), "error": str(e)},
                )
            )

    def backup_config(self) -> Path:
        """Create a backup of the current configuration."""
        result = self._backup_config_safe()
        return result.unwrap()

    def _backup_config_safe(self) -> Result[Path, ConfigurationError]:
        """Safely create a backup with Result pattern."""
        try:
            if not self.config_path.exists():
                return Result.failure(
                    ConfigurationError(
                        f"Configuration file does not exist: {self.config_path}",
                        context={"path": str(self.config_path)},
                    )
                )

            timestamp = generate_timestamp().replace(":", "-").replace(".", "-")
            # Create backup directory if it doesn't exist
            backup_dir = self.config_path.parent / "fca_config_backups"
            backup_dir.mkdir(exist_ok=True)
            backup_path = (
                backup_dir / f"{self.config_path.stem}.backup.{timestamp}.yaml"
            )

            shutil.copy2(self.config_path, backup_path)
            self.console.print(f"📋 Config backed up to: {backup_path}")

            # Clean up old backups (keep only last 5)
            self._cleanup_old_backups()

            return Result.success(backup_path)
        except Exception as e:
            return Result.failure(
                ConfigurationError(
                    f"Failed to create backup: {e}",
                    context={"source": str(self.config_path), "error": str(e)},
                )
            )

    def _cleanup_old_backups(self, keep_count: int = 5) -> None:
        """Clean up old backup files created by ConfigUpdater, keeping only the most recent ones."""
        try:
            backup_dir = self.config_path.parent / "fca_config_backups"
            if not backup_dir.exists():
                return

            # Pattern for ConfigUpdater backups: filename.backup.timestamp.yaml
            backup_pattern = f"{self.config_path.stem}.backup.*.yaml"
            backup_files = list(backup_dir.glob(backup_pattern))

            if len(backup_files) > keep_count:
                # Sort by modification time (newest first)
                backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

                # Remove old backups
                for old_backup in backup_files[keep_count:]:
                    try:
                        old_backup.unlink()
                        self.console.print(
                            f"🗑️  Removed old backup: {old_backup.name}", style="dim"
                        )
                    except OSError:
                        # Ignore errors when cleaning up old backups
                        pass
        except OSError:
            # Don't fail the main operation if backup cleanup fails
            pass

    def add_system(
        self,
        system_name: str,
        description: Optional[str] = None,
        backup: bool = True,
    ) -> None:
        """Add a new system to the configuration with validation."""
        # Validate system name
        name_result = Validator.validate_system_name(system_name)
        if name_result.is_failure:
            name_result.unwrap()  # This will raise the error

        # Validate description if provided
        if description:
            desc_result = Validator.validate_description(description)
            if desc_result.is_failure:
                desc_result.unwrap()  # This will raise the error

        if backup and self.config_path.exists():
            self.backup_config()

        # Add system to config
        validated_name = name_result.value
        if validated_name is None:
            raise ValidationError(
                "Validated name should not be None after successful validation"
            )
        self.config.add_system(validated_name, description or "")

        # Save updated config
        self._save_config_atomically()

        self.console.print(f"✅ Added system: {name_result.value}")

    def add_module(
        self,
        system_name: str,
        module_name: str,
        description: Optional[str] = None,
        backup: bool = True,
    ) -> None:
        """Add a new module to a system with validation."""
        # Validate system name
        system_result = Validator.validate_system_name(system_name)
        if system_result.is_failure:
            system_result.unwrap()  # This will raise the error

        # Validate module name
        module_result = Validator.validate_module_name(module_name)
        if module_result.is_failure:
            module_result.unwrap()  # This will raise the error

        # Validate description if provided
        if description:
            desc_result = Validator.validate_description(description)
            if desc_result.is_failure:
                desc_result.unwrap()  # This will raise the error

        if backup and self.config_path.exists():
            self.backup_config()

        # Add module to config
        validated_system = system_result.value
        validated_module = module_result.value
        if validated_system is None:
            raise ValidationError(
                "Validated system should not be None after successful validation"
            )
        if validated_module is None:
            raise ValidationError(
                "Validated module should not be None after successful validation"
            )
        self.config.add_module(validated_system, validated_module, description or "")

        # Save updated config
        self._save_config_atomically()

        self.console.print(
            f"✅ Added module: {module_result.value} to system: {system_result.value}"
        )

    def add_component(
        self,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
        file_path: Optional[Path] = None,
        backup: bool = True,
    ) -> None:
        """Add a new component to a module with comprehensive validation."""
        # Validate all inputs
        validation_result = Validator.validate_component_creation(
            system_name=system_name,
            module_name=module_name,
            layer=layer,
            component_type=component_type,
            component_name=component_name,
            file_path=file_path,
        )

        if validation_result.is_failure:
            validation_result.unwrap()  # This will raise the error

        if backup and self.config_path.exists():
            self.backup_config()

        # Add component to config using validated data
        validated_data = validation_result.value
        if validated_data is None:
            raise ConfigurationError("Validation result is None")

        self.config.add_component(
            system_name=validated_data["system_name"],
            module_name=validated_data["module_name"],
            layer=validated_data["layer"],
            component_type=validated_data["component_type"],
            component_name=validated_data["component_name"],
            file_path=(
                str(validated_data["file_path"])
                if "file_path" in validated_data and validated_data["file_path"]
                else None
            ),
        )

        # Save updated config
        self._save_config_atomically()

        self.console.print(
            f"✅ Added component: {component_name} ({component_type}) "
            f"to {system_name}/{module_name}/{layer}"
        )

    def update_system_timestamp(self, system_name: str, backup: bool = True) -> None:
        """Update the timestamp for a system and cascade to project."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Update system timestamp
        if system_name in self.config.project.systems:
            current_time = generate_timestamp()
            self.config.project.systems[system_name].updated_at = current_time
            self.config.project.updated_at = current_time

        # Save updated config
        self._save_config_atomically()

    def update_module_timestamp(
        self, system_name: str, module_name: str, backup: bool = True
    ) -> None:
        """Update the timestamp for a module and cascade to system and project."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Update module, system, and project timestamps
        if (
            system_name in self.config.project.systems
            and module_name in self.config.project.systems[system_name].modules
        ):
            current_time = generate_timestamp()
            self.config.project.systems[system_name].modules[
                module_name
            ].updated_at = current_time
            self.config.project.systems[system_name].updated_at = current_time
            self.config.project.updated_at = current_time

        # Save updated config
        self._save_config_atomically()

    def update_project_metadata(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        backup: bool = True,
    ) -> None:
        """Update project metadata."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Update project metadata
        current_time = generate_timestamp()

        if name is not None:
            self.config.project.name = name
        if description is not None:
            self.config.project.description = description
        if version is not None:
            self.config.project.version = version

        self.config.project.updated_at = current_time

        # Save updated config
        self._save_config_atomically()

        self.console.print("✅ Updated project metadata")

    def remove_system(self, system_name: str, backup: bool = True) -> None:
        """Remove a system from the configuration."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Remove system
        if system_name in self.config.project.systems:
            del self.config.project.systems[system_name]
            self.config.project.updated_at = generate_timestamp()

        # Save updated config
        self._save_config_atomically()

        self.console.print(f"🗑️ Removed system: {system_name}")

    def remove_module(
        self, system_name: str, module_name: str, backup: bool = True
    ) -> None:
        """Remove a module from a system."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Remove module
        if (
            system_name in self.config.project.systems
            and module_name in self.config.project.systems[system_name].modules
        ):
            del self.config.project.systems[system_name].modules[module_name]
            current_time = generate_timestamp()
            self.config.project.systems[system_name].updated_at = current_time
            self.config.project.updated_at = current_time

        # Save updated config
        self._save_config_atomically()

        self.console.print(
            f"🗑️ Removed module: {module_name} from system: {system_name}"
        )

    def remove_component(
        self,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
        backup: bool = True,
    ) -> None:
        """Remove a component from a module."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Navigate to the component and remove it
        try:
            system = self.config.project.systems[system_name]
            module = system.modules[module_name]
            layer_components = getattr(module.components, layer)
            component_list = getattr(layer_components, component_type)

            # Find and remove the component
            component_list[:] = [
                comp for comp in component_list if comp.name != component_name
            ]

            # Update timestamps
            current_time = generate_timestamp()
            module.updated_at = current_time
            system.updated_at = current_time
            self.config.project.updated_at = current_time

        except (KeyError, AttributeError) as e:
            raise ConfigurationError(f"Component not found: {e}")

        # Save updated config
        self._save_config_atomically()

        self.console.print(
            f"🗑️ Removed component: {component_name} ({component_type}) "
            f"from {system_name}/{module_name}/{layer}"
        )

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        summary: Dict[str, Any] = {
            "project": {
                "name": self.config.project.name,
                "version": self.config.project.version,
                "created_at": self.config.project.created_at,
                "updated_at": self.config.project.updated_at,
            },
            "systems": {},
        }

        for system_name, system in self.config.project.systems.items():
            summary["systems"][system_name] = {
                "description": system.description,
                "created_at": system.created_at,
                "updated_at": system.updated_at,
                "modules": list(system.modules.keys()),
            }

        return summary

    def _save_config_atomically(self) -> None:
        """Save configuration atomically to prevent corruption."""
        result = self._save_config_atomically_safe()
        result.unwrap()

    def _save_config_atomically_safe(self) -> Result[None, ConfigurationError]:
        """Safely save configuration with Result pattern."""
        temp_path: Optional[Path] = None
        try:
            # Write to temporary file first
            temp_path = self.config_path.with_suffix(".tmp")
            self.config.save_to_file(temp_path)

            # Atomic move
            temp_path.replace(self.config_path)
            return Result.success(None)

        except Exception as e:
            # Clean up temp file if it exists
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass  # Ignore cleanup errors
            return Result.failure(
                ConfigurationError(
                    f"Failed to save configuration: {e}",
                    context={"config_path": str(self.config_path), "error": str(e)},
                )
            )

    def reload_config(self) -> None:
        """Reload configuration from file."""
        self._config = None  # Force reload on next access
