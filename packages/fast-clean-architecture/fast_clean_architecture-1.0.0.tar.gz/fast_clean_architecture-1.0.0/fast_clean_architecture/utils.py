"""Utility functions for Fast Clean Architecture."""

import keyword
import re
import urllib.parse
import unicodedata
import threading
import fcntl
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def generate_timestamp() -> str:
    """Generate ISO 8601 timestamp in UTC with validation."""
    try:
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        # Validate the timestamp format
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return timestamp
    except Exception as e:
        raise ValueError(f"Failed to generate valid timestamp: {e}")


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


# File locking utilities
_file_locks = {}
_locks_lock = threading.Lock()


def get_file_lock(file_path: Union[str, Path]) -> threading.Lock:
    """Get or create a lock for a specific file path."""
    file_path_str = str(file_path)
    with _locks_lock:
        if file_path_str not in _file_locks:
            _file_locks[file_path_str] = threading.Lock()
        return _file_locks[file_path_str]


def secure_file_operation(file_path: Union[str, Path], operation_func, *args, **kwargs):
    """Execute file operation with proper locking."""
    lock = get_file_lock(file_path)
    with lock:
        return operation_func(*args, **kwargs)


def sanitize_error_message(
    error_msg: str, sensitive_info: Optional[List[str]] = None
) -> str:
    """Sanitize error messages to prevent information disclosure."""
    if sensitive_info is None:
        sensitive_info = []

    # Add common sensitive patterns
    sensitive_patterns = [
        r"/Users/[^/\s]+",  # User home directories
        r"/home/[^/\s]+",  # Linux home directories
        r"C:\\Users\\[^\\\s]+",  # Windows user directories
        r"/tmp/[^/\s]+",  # Temporary directories
        r"/var/[^/\s]+",  # System directories
        r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",  # IP addresses
    ]

    # Add user-provided sensitive info
    sensitive_patterns.extend(sensitive_info)

    sanitized_msg = error_msg
    for pattern in sensitive_patterns:
        sanitized_msg = re.sub(pattern, "[REDACTED]", sanitized_msg)

    return sanitized_msg


def create_secure_error(error_type: str, operation: str, details: Optional[str] = None):
    """Create a secure error message without exposing sensitive information."""
    from fast_clean_architecture.exceptions import ValidationError

    base_msg = f"Failed to {operation}"

    if details:
        # Sanitize details before including
        safe_details = sanitize_error_message(details)
        return ValidationError(f"{base_msg}: {safe_details}")

    return ValidationError(base_msg)


def to_snake_case(name: str) -> str:
    """Convert string to snake_case."""
    # Replace hyphens and spaces with underscores
    name = re.sub(r"[-\s]+", "_", name)
    # Handle sequences of uppercase letters followed by lowercase letters
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    # Insert underscore before uppercase letters that follow lowercase letters or digits
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def to_pascal_case(name: str) -> str:
    """Convert string to PascalCase."""
    # First convert to snake_case to normalize, then split and capitalize
    snake_name = to_snake_case(name)
    words = snake_name.split("_")
    return "".join(word.capitalize() for word in words if word)


def to_camel_case(name: str) -> str:
    """Convert string to camelCase."""
    pascal = to_pascal_case(name)
    return pascal[0].lower() + pascal[1:] if pascal else ""


def pluralize(word: str) -> str:
    """Simple pluralization for English words."""
    # Handle irregular plurals
    irregular_plurals = {
        "person": "people",
        "child": "children",
        "mouse": "mice",
        "foot": "feet",
        "tooth": "teeth",
        "goose": "geese",
        "man": "men",
        "woman": "women",
    }

    # Handle uncountable nouns
    uncountable = {"data", "sheep", "fish", "deer", "species", "series"}

    if word.lower() in uncountable:
        return word

    if word.lower() in irregular_plurals:
        return irregular_plurals[word.lower()]

    # Regular pluralization rules
    if word.endswith("y") and len(word) > 1 and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    elif word.endswith(("s", "sh", "ch", "x", "z")):
        return word + "es"
    elif word.endswith("f"):
        return word[:-1] + "ves"
    elif word.endswith("fe"):
        return word[:-2] + "ves"
    else:
        return word + "s"


def validate_python_identifier(name: str) -> bool:
    """Validate if string is a valid Python identifier."""
    return (
        name.isidentifier()
        and not keyword.iskeyword(name)
        and not name.startswith("__")
    )


def sanitize_name(name: str) -> str:
    """Sanitize name to be a valid Python identifier."""
    # Strip whitespace
    name = name.strip()

    # Remove invalid characters except letters, numbers, spaces, hyphens, underscores
    sanitized = re.sub(r"[^a-zA-Z0-9\s\-_]", "", name)

    # Convert to snake_case
    sanitized = to_snake_case(sanitized)

    # Remove leading/trailing underscores and collapse multiple underscores
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")

    # Handle names that start with numbers
    if sanitized and sanitized[0].isdigit():
        # Remove leading numbers
        sanitized = re.sub(r"^[0-9_]+", "", sanitized)

    # Ensure it's not empty
    if not sanitized:
        sanitized = "component"

    return sanitized


def validate_name(name: str) -> None:
    """Validate component name for security and correctness.

    Args:
        name: The name to validate

    Raises:
        ValueError: If the name is invalid
        TypeError: If the name is not a string
        ValidationError: If the name contains security risks
    """
    from fast_clean_architecture.exceptions import ValidationError

    # Check for None or non-string types
    if name is None:
        raise TypeError("Name cannot be None")

    if not isinstance(name, str):
        raise TypeError(f"Name must be a string, got {type(name).__name__}")

    # Check for empty or whitespace-only names
    if not name or not name.strip():
        raise ValueError("Name cannot be empty or whitespace-only")

    # Check length limits
    if len(name) > 100:
        raise ValueError(f"Name too long: {len(name)} characters (max 100)")

    # Check for path traversal attempts (including encoded and Unicode variants)
    # First, decode any URL-encoded sequences
    try:
        decoded_name = urllib.parse.unquote(name)
        # Apply Unicode normalization to handle Unicode attacks
        normalized_name = unicodedata.normalize("NFKC", decoded_name)
    except Exception:
        # If decoding fails, treat as suspicious
        raise ValidationError(
            f"Invalid component name: suspicious encoding detected in '{name}'"
        )

    # Check for path traversal in original, decoded, and normalized forms
    names_to_check = [name, decoded_name, normalized_name]
    for check_name in names_to_check:
        if ".." in check_name or "/" in check_name or "\\" in check_name:
            raise ValidationError(
                f"Invalid component name: path traversal detected in '{name}'"
            )

    # Check for encoded path traversal sequences
    encoded_patterns = [
        "%2e%2e",
        "%2E%2E",  # .. encoded
        "%2f",
        "%2F",  # / encoded
        "%5c",
        "%5C",  # \ encoded
        "%252e",
        "%252E",  # double-encoded .
        "%252f",
        "%252F",  # double-encoded /
        "%255c",
        "%255C",  # double-encoded \
    ]
    name_lower = name.lower()
    for pattern in encoded_patterns:
        if pattern in name_lower:
            raise ValidationError(
                f"Invalid component name: encoded path traversal detected in '{name}'"
            )

    # Check for Unicode path traversal variants
    unicode_dots = ["\u002e", "\uff0e", "\u2024", "\u2025", "\u2026"]
    unicode_slashes = ["\u002f", "\uff0f", "\u2044", "\u29f8"]
    unicode_backslashes = ["\u005c", "\uff3c", "\u29f5", "\u29f9"]

    for dot in unicode_dots:
        for dot2 in unicode_dots:
            if dot + dot2 in name:
                raise ValidationError(
                    f"Invalid component name: Unicode path traversal detected in '{name}'"
                )

    for slash in unicode_slashes + unicode_backslashes:
        if slash in name:
            raise ValidationError(
                f"Invalid component name: Unicode path separator detected in '{name}'"
            )

    # Check for shell injection attempts
    dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "<", ">", "'", '"']
    for char in dangerous_chars:
        if char in name:
            raise ValidationError(
                f"Invalid component name: dangerous character '{char}' in '{name}'"
            )

    # Check for special characters that could cause issues
    invalid_chars = [
        "@",
        "#",
        "%",
        "*",
        "+",
        "=",
        "?",
        "[",
        "]",
        "{",
        "}",
        ":",
        " ",
        "\t",
        "\n",
        "\r",
    ]
    for char in invalid_chars:
        if char in name:
            raise ValidationError(
                f"Invalid component name: invalid character '{char}' in '{name}'"
            )

    # Check for unicode control characters and dangerous unicode
    for char in name:
        if ord(char) < 32 or ord(char) in [
            0x202E,
            0x200B,
            0xFEFF,
            0x2028,
            0x2029,
            0xFFFE,
            0xFFFF,
        ]:
            raise ValidationError(
                f"Invalid component name: dangerous unicode character in '{name}'"
            )

    # Check for environment variable patterns
    if name.startswith("$") or "${" in name or "`" in name:
        raise ValidationError(
            f"Invalid component name: environment variable pattern detected in '{name}'"
        )

    # Check if name starts with a digit (invalid for Python identifiers)
    if name and name[0].isdigit():
        raise ValidationError(
            f"Invalid component name: '{name}' cannot start with a digit"
        )

    # Ensure it would make a valid Python identifier after sanitization
    sanitized = sanitize_name(name)
    if not validate_python_identifier(sanitized):
        raise ValidationError(
            f"Invalid component name: '{name}' cannot be converted to valid Python identifier"
        )


def get_template_variables(
    system_name: str,
    module_name: str,
    component_name: str,
    component_type: str,
    **kwargs,
) -> dict:
    """Generate template variables for rendering."""
    snake_name = to_snake_case(component_name)
    pascal_name = to_pascal_case(component_name)
    camel_name = to_camel_case(component_name)

    # System and module variations
    system_snake = to_snake_case(system_name)
    system_pascal = to_pascal_case(system_name)
    system_camel = to_camel_case(system_name)

    module_snake = to_snake_case(module_name)
    module_pascal = to_pascal_case(module_name)
    module_camel = to_camel_case(module_name)

    component_type_snake = to_snake_case(component_type)
    component_type_pascal = to_pascal_case(component_type)
    component_type_camel = to_camel_case(component_type)

    variables = {
        # System variations
        "system_name": system_snake,
        "SystemName": system_pascal,
        "system_name_camel": system_camel,
        # Module variations
        "module_name": module_snake,
        "ModuleName": module_pascal,
        "module_name_camel": module_camel,
        # Component variations
        "component_name": snake_name,
        "ComponentName": pascal_name,
        "component_name_camel": camel_name,
        # Component type variations
        "component_type": component_type_snake,
        "ComponentType": component_type_pascal,
        "component_type_camel": component_type_camel,
        # Common naming variations
        "entity_name": snake_name,
        "EntityName": pascal_name,
        "entity_name_camel": camel_name,
        "repository_name": snake_name,
        "RepositoryName": pascal_name,
        "repository_name_camel": camel_name,
        "service_name": snake_name,
        "ServiceName": pascal_name,
        "service_name_camel": camel_name,
        "router_name": snake_name,
        "RouterName": pascal_name,
        "router_name_camel": camel_name,
        "schema_name": snake_name,
        "SchemaName": pascal_name,
        "schema_name_camel": camel_name,
        "command_name": snake_name,
        "CommandName": pascal_name,
        "command_name_camel": camel_name,
        "query_name": snake_name,
        "QueryName": pascal_name,
        "query_name_camel": camel_name,
        "model_name": snake_name,
        "ModelName": pascal_name,
        "model_name_camel": camel_name,
        "value_object_name": snake_name,
        "ValueObjectName": pascal_name,
        "value_object_name_camel": camel_name,
        "external_service_name": snake_name,
        "ExternalServiceName": pascal_name,
        "external_service_name_camel": camel_name,
        # File naming
        "entity_file": f"{snake_name}.py",
        "repository_file": f"{snake_name}_repository.py",
        "service_file": f"{snake_name}_service.py",
        "router_file": f"{snake_name}_router.py",
        "schema_file": f"{snake_name}_schemas.py",
        "command_file": f"{snake_name}.py",
        "query_file": f"{snake_name}.py",
        "model_file": f"{snake_name}_model.py",
        "value_object_file": f"{snake_name}_value_object.py",
        "external_service_file": f"{snake_name}_external_service.py",
        # Resource naming (for APIs)
        "resource_name": snake_name,
        "resource_name_plural": pluralize(snake_name),
        # Descriptions
        "entity_description": f"{snake_name.replace('_', ' ')}",
        "service_description": f"{snake_name.replace('_', ' ')} operations",
        "module_description": f"{module_snake.replace('_', ' ')} module",
        # Import paths (for better import management)
        "domain_import_path": f"{system_snake}.{module_snake}.domain",
        "application_import_path": f"{system_snake}.{module_snake}.application",
        "infrastructure_import_path": f"{system_snake}.{module_snake}.infrastructure",
        "presentation_import_path": f"{system_snake}.{module_snake}.presentation",
        # Relative imports
        "entity_import": f"..domain.entities.{snake_name}",
        "repository_import": f"..domain.repositories.{snake_name}_repository",
        "service_import": f"..application.services.{snake_name}_service",
        # Timestamp for file generation
        "generated_at": generate_timestamp(),
        "generator_version": "1.0.0",
        # Additional naming patterns
        "table_name": pluralize(snake_name),
        "collection_name": pluralize(snake_name),
        "endpoint_prefix": f"/{pluralize(snake_name.replace('_', '-'))}",
        # Type hints
        "entity_type": pascal_name,
        "repository_type": f"{pascal_name}Repository",
        "service_type": f"{pascal_name}Service",
    }

    # Add any additional variables
    variables.update(kwargs)

    return variables


def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if it doesn't."""
    path.mkdir(parents=True, exist_ok=True)


def get_layer_from_path(path: str) -> Optional[str]:
    """Extract layer name from file path."""
    layers = ["domain", "application", "infrastructure", "presentation"]
    path_parts = Path(path).parts

    for layer in layers:
        if layer in path_parts:
            return layer

    return None


def get_component_type_from_path(path: str) -> Optional[str]:
    """Extract component type from file path."""
    component_types = [
        "entities",
        "repositories",
        "value_objects",  # domain
        "services",
        "commands",
        "queries",  # application
        "models",
        "external",
        "internal",  # infrastructure
        "api",
        "schemas",  # presentation
    ]

    path_parts = Path(path).parts

    for comp_type in component_types:
        if comp_type in path_parts:
            return comp_type

    return None


def parse_location_path(location: str) -> dict[str, str]:
    """Parse location path to extract system, module, layer, and component type.

    Args:
        location: Path like 'user_management/authentication/domain/entities'

    Returns:
        Dict with keys: system_name, module_name, layer, component_type
    """
    from .exceptions import ValidationError

    path_parts = Path(location).parts

    if len(path_parts) != 4:
        raise ValidationError(
            f"Location must be in format: {{system}}/{{module}}/{{layer}}/{{component_type}}"
        )

    system_name = path_parts[0]
    module_name = path_parts[1]
    layer = path_parts[2]
    component_type = path_parts[3]

    # Validate layer
    valid_layers = ["domain", "application", "infrastructure", "presentation"]
    if layer not in valid_layers:
        raise ValidationError(f"Invalid layer: {layer}. Must be one of {valid_layers}")

    # Validate component type based on layer
    layer_components = {
        "domain": ["entities", "repositories", "value_objects"],
        "application": ["services", "commands", "queries"],
        "infrastructure": ["models", "repositories", "external", "internal"],
        "presentation": ["api", "schemas"],
    }

    if component_type not in layer_components[layer]:
        raise ValidationError(
            f"Invalid component type '{component_type}' for layer '{layer}'. "
            f"Valid types: {layer_components[layer]}"
        )

    return {
        "system_name": system_name,
        "module_name": module_name,
        "layer": layer,
        "component_type": component_type,
    }
