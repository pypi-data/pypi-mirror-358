"""Configuration updater for managing fca-config.yaml updates."""

import shutil
from pathlib import Path
from typing import Optional, Dict, Any

from rich.console import Console

from ..config import Config
from ..utils import generate_timestamp
from ..exceptions import ConfigurationError


class ConfigUpdater:
    """Handles updates to the fca-config.yaml file with proper timestamp management."""

    def __init__(self, config_path: Path, console: Console = None):
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
        if self.config_path.exists():
            return Config.load_from_file(self.config_path)
        else:
            # Create default config if it doesn't exist
            config = Config.create_default()
            config.save_to_file(self.config_path)
            return config

    def backup_config(self) -> Path:
        """Create a backup of the current configuration."""
        if not self.config_path.exists():
            raise ConfigurationError(
                f"Configuration file does not exist: {self.config_path}"
            )

        timestamp = generate_timestamp().replace(":", "-").replace(".", "-")
        backup_path = self.config_path.with_suffix(f".backup.{timestamp}.yaml")

        shutil.copy2(self.config_path, backup_path)
        self.console.print(f"📋 Config backed up to: {backup_path}")
        return backup_path

    def add_system(
        self,
        system_name: str,
        description: Optional[str] = None,
        backup: bool = True,
    ) -> None:
        """Add a new system to the configuration."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Add system to config
        self.config.add_system(system_name, description)

        # Save updated config
        self._save_config_atomically()

        self.console.print(f"✅ Added system: {system_name}")

    def add_module(
        self,
        system_name: str,
        module_name: str,
        description: Optional[str] = None,
        backup: bool = True,
    ) -> None:
        """Add a new module to a system."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Add module to config
        self.config.add_module(system_name, module_name, description)

        # Save updated config
        self._save_config_atomically()

        self.console.print(f"✅ Added module: {module_name} to system: {system_name}")

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
        """Add a new component to a module."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Add component to config
        self.config.add_component(
            system_name=system_name,
            module_name=module_name,
            layer=layer,
            component_type=component_type,
            component_name=component_name,
            file_path=str(file_path) if file_path else None,
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
        summary = {
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
        try:
            # Write to temporary file first
            temp_path = self.config_path.with_suffix(".tmp")
            self.config.save_to_file(temp_path)

            # Atomic move
            temp_path.replace(self.config_path)

        except Exception as e:
            # Clean up temp file if it exists
            temp_path = self.config_path.with_suffix(".tmp")
            if temp_path.exists():
                temp_path.unlink()
            raise ConfigurationError(f"Failed to save configuration: {e}")

    def reload_config(self) -> None:
        """Reload configuration from file."""
        self._config = None  # Force reload on next access
