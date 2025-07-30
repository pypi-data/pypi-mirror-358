"""Validation utilities for Fast Clean Architecture."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Set, Union

from .exceptions import Result, SecurityError, ValidationError


class ValidationRules:
    """Centralized validation rules and patterns."""

    # Component naming patterns
    COMPONENT_NAME_PATTERN: Pattern[str] = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")
    SYSTEM_NAME_PATTERN: Pattern[str] = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
    MODULE_NAME_PATTERN: Pattern[str] = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")

    # Security patterns
    DANGEROUS_PATH_PATTERNS: List[Pattern[str]] = [
        re.compile(r"\.\."),  # Path traversal
        re.compile(r"^/etc/|^/root/|^/proc/|^/sys/"),  # Dangerous system paths only
        re.compile(r"^~"),  # Home directory
        re.compile(r"\$\{"),  # Variable expansion
        re.compile(r"\$\("),  # Command substitution
    ]

    # Valid component types and layers
    VALID_LAYERS: Set[str] = {"domain", "application", "infrastructure", "presentation"}

    VALID_COMPONENT_TYPES: Set[str] = {
        "entities",
        "repositories",
        "services",
        "controllers",
        "models",
        "views",
        "adapters",
        "gateways",
        "external",
    }

    # File extension validation
    ALLOWED_EXTENSIONS: Set[str] = {
        ".py",
        ".yaml",
        ".yml",
        ".json",
        ".md",
        ".txt",
        ".toml",
    }


class Validator:
    """Main validation class with comprehensive checks."""

    @staticmethod
    def validate_component_name(name: str) -> Result[str, ValidationError]:
        """Validate component name format."""
        if not name:
            return Result.failure(
                ValidationError(
                    "Component name cannot be empty", context={"name": name}
                )
            )

        if not ValidationRules.COMPONENT_NAME_PATTERN.match(name):
            return Result.failure(
                ValidationError(
                    f"Invalid component name format: {name}. Must start with letter and contain only letters, numbers, and underscores.",
                    context={
                        "name": name,
                        "pattern": ValidationRules.COMPONENT_NAME_PATTERN.pattern,
                    },
                )
            )

        if len(name) > 50:
            return Result.failure(
                ValidationError(
                    f"Component name too long: {len(name)} characters. Maximum 50 allowed.",
                    context={"name": name, "length": len(name)},
                )
            )

        return Result.success(name)

    @staticmethod
    def validate_system_name(name: str) -> Result[str, ValidationError]:
        """Validate system name format."""
        if not name:
            return Result.failure(
                ValidationError("System name cannot be empty", context={"name": name})
            )

        if not ValidationRules.SYSTEM_NAME_PATTERN.match(name):
            return Result.failure(
                ValidationError(
                    f"Invalid system name format: {name}. Must start with letter and contain only letters, numbers, underscores, and hyphens.",
                    context={
                        "name": name,
                        "pattern": ValidationRules.SYSTEM_NAME_PATTERN.pattern,
                    },
                )
            )

        return Result.success(name)

    @staticmethod
    def validate_module_name(name: str) -> Result[str, ValidationError]:
        """Validate module name format."""
        if not name:
            return Result.failure(
                ValidationError("Module name cannot be empty", context={"name": name})
            )

        if not ValidationRules.MODULE_NAME_PATTERN.match(name):
            return Result.failure(
                ValidationError(
                    f"Invalid module name format: {name}. Must start with letter and contain only letters, numbers, and underscores.",
                    context={
                        "name": name,
                        "pattern": ValidationRules.MODULE_NAME_PATTERN.pattern,
                    },
                )
            )

        return Result.success(name)

    @staticmethod
    def validate_layer(layer: str) -> Result[str, ValidationError]:
        """Validate layer name."""
        if layer not in ValidationRules.VALID_LAYERS:
            return Result.failure(
                ValidationError(
                    f"Invalid layer: {layer}. Must be one of: {', '.join(sorted(ValidationRules.VALID_LAYERS))}",
                    context={
                        "layer": layer,
                        "valid_layers": list(ValidationRules.VALID_LAYERS),
                    },
                )
            )

        return Result.success(layer)

    @staticmethod
    def validate_component_type(component_type: str) -> Result[str, ValidationError]:
        """Validate component type."""
        if component_type not in ValidationRules.VALID_COMPONENT_TYPES:
            return Result.failure(
                ValidationError(
                    f"Invalid component type: {component_type}. Must be one of: {', '.join(sorted(ValidationRules.VALID_COMPONENT_TYPES))}",
                    context={
                        "component_type": component_type,
                        "valid_types": list(ValidationRules.VALID_COMPONENT_TYPES),
                    },
                )
            )

        return Result.success(component_type)

    @staticmethod
    def validate_file_path(file_path: Union[str, Path]) -> Result[Path, SecurityError]:
        """Validate file path for security issues."""
        path_str = str(file_path)

        # Check for dangerous patterns
        for pattern in ValidationRules.DANGEROUS_PATH_PATTERNS:
            if pattern.search(path_str):
                return Result.failure(
                    SecurityError(
                        f"Potentially dangerous path pattern detected: {path_str}",
                        context={"path": path_str, "pattern": pattern.pattern},
                    )
                )

        # Convert to Path object
        try:
            path_obj = Path(path_str)
        except Exception as e:
            return Result.failure(
                SecurityError(
                    f"Invalid path format: {path_str}",
                    context={"path": path_str, "error": str(e)},
                )
            )

        # Check file extension
        if (
            path_obj.suffix
            and path_obj.suffix not in ValidationRules.ALLOWED_EXTENSIONS
        ):
            return Result.failure(
                SecurityError(
                    f"File extension not allowed: {path_obj.suffix}",
                    context={
                        "path": path_str,
                        "extension": path_obj.suffix,
                        "allowed": list(ValidationRules.ALLOWED_EXTENSIONS),
                    },
                )
            )

        return Result.success(path_obj)

    @staticmethod
    def validate_description(
        description: str, max_length: int = 500
    ) -> Result[str, Union[ValidationError, SecurityError]]:
        """Validate description text."""
        if len(description) > max_length:
            return Result.failure(
                ValidationError(
                    f"Description too long: {len(description)} characters. Maximum {max_length} allowed.",
                    context={
                        "description": description[:100] + "...",
                        "length": len(description),
                        "max_length": max_length,
                    },
                )
            )

        # Check for potentially dangerous content
        dangerous_patterns = ["<script", "${", "$(", "javascript:"]
        for pattern in dangerous_patterns:
            if pattern.lower() in description.lower():
                return Result.failure(
                    SecurityError(
                        f"Potentially dangerous content in description: {pattern}",
                        context={
                            "description": description[:100] + "...",
                            "pattern": pattern,
                        },
                    )
                )

        return Result.success(description)

    @classmethod
    def validate_component_creation(
        cls,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
        file_path: Optional[Union[str, Path]] = None,
        description: Optional[str] = None,
    ) -> Result[Dict[str, Any], Union[ValidationError, SecurityError]]:
        """Comprehensive validation for component creation."""

        # Validate all required fields
        system_validation = cls.validate_system_name(system_name)
        if system_validation.is_failure:
            return system_validation  # type: ignore

        module_validation = cls.validate_module_name(module_name)
        if module_validation.is_failure:
            return module_validation  # type: ignore

        layer_validation = cls.validate_layer(layer)
        if layer_validation.is_failure:
            return layer_validation  # type: ignore

        component_type_validation = cls.validate_component_type(component_type)
        if component_type_validation.is_failure:
            return component_type_validation  # type: ignore

        component_name_validation = cls.validate_component_name(component_name)
        if component_name_validation.is_failure:
            return component_name_validation  # type: ignore

        # Validate optional fields
        validated_file_path = None
        if file_path is not None:
            file_validation = cls.validate_file_path(file_path)
            if file_validation.is_failure:
                return file_validation  # type: ignore
            else:
                validated_file_path = file_validation.value

        if description is not None:
            description_validation = cls.validate_description(description)
            if description_validation.is_failure:
                return description_validation  # type: ignore

        # Return validated data
        validated_data = {
            "system_name": system_name,
            "module_name": module_name,
            "layer": layer,
            "component_type": component_type,
            "component_name": component_name,
        }

        if validated_file_path is not None:
            validated_data["file_path"] = str(validated_file_path)

        if description is not None:
            validated_data["description"] = description

        return Result.success(validated_data)
