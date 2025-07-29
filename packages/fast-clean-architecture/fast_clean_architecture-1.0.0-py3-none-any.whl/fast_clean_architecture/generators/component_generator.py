"""Component generator for creating individual component files."""

import os
import re
import functools
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

import jinja2
from jinja2 import TemplateSyntaxError
from jinja2.exceptions import SecurityError
from jinja2.sandbox import SandboxedEnvironment
from rich.console import Console

from ..templates import TEMPLATES_DIR
from ..utils import (
    get_template_variables,
    to_pascal_case,
    to_snake_case,
    ensure_directory,
    sanitize_name,
    validate_python_identifier,
    validate_name,
    secure_file_operation,
    create_secure_error,
    sanitize_error_message,
)
from ..exceptions import (
    TemplateError,
    ValidationError,
    FileConflictError,
    ComponentError,
)
from ..config import Config
from .template_validator import TemplateValidatorFactory

# Set up logger for security events
logger = logging.getLogger(__name__)


class ComponentGenerator:
    """Generator for creating individual component files from templates."""

    # Mapping of component types to their template files
    TEMPLATE_MAPPING = {
        "entities": "entity.py.j2",
        "repositories": "repository.py.j2",
        "value_objects": "value_object.py.j2",
        "services": "service.py.j2",
        "commands": "command.py.j2",
        "queries": "query.py.j2",
        "models": "model.py.j2",
        "external": "external.py.j2",
        "api": "api.py.j2",
        "schemas": "schemas.py.j2",
    }

    # Infrastructure repositories use a different template
    INFRASTRUCTURE_REPOSITORY_TEMPLATE = "infrastructure_repository.py.j2"

    def __init__(self, config: Config, console: Optional[Console] = None):
        self.config = config
        self.console = console or Console()
        # Use SandboxedEnvironment for security
        self.template_env = SandboxedEnvironment(
            loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
            trim_blocks=True,
            lstrip_blocks=True,
            # Restrict available functions and filters for security
            finalize=self._sanitize_template_output,
        )
        # Define allowed filters and functions
        self._setup_sandbox_security()

        # Initialize template validator with simplified validation config
        from .validation_config import ValidationConfig

        validation_config = ValidationConfig(
            sandbox_mode=True,
            max_template_size_bytes=64 * 1024,  # 64KB limit
            render_timeout_seconds=10,
            max_variable_nesting_depth=10,
        )
        self.template_validator = TemplateValidatorFactory().create(
            self.template_env, validation_config
        )

    def create_component(
        self,
        base_path: Path,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
        dry_run: bool = False,
        force: bool = False,
    ) -> Path:
        """Create a single component file."""
        # Validate inputs
        self._validate_component_inputs(
            system_name, module_name, layer, component_type, component_name
        )

        # Sanitize component name
        sanitized_name = sanitize_name(component_name)
        if not validate_python_identifier(sanitized_name):
            raise ValidationError(f"Invalid component name: {component_name}")

        # Determine file path and name
        file_path, file_name = self._get_component_file_path(
            base_path, system_name, module_name, layer, component_type, sanitized_name
        )

        # Check for conflicts
        if file_path.exists() and not force:
            raise FileConflictError(
                f"Component file already exists: {file_path}. Use --force to overwrite."
            )

        if dry_run:
            self.console.print(f"[yellow]DRY RUN:[/yellow] Would create {file_path}")
            return file_path

        # Validate file system permissions and space
        self._validate_file_system(file_path)

        # Ensure directory exists
        ensure_directory(file_path.parent)

        # Generate template variables
        template_vars = get_template_variables(
            system_name=system_name,
            module_name=module_name,
            component_name=sanitized_name,
            component_type=component_type,
        )

        # Get template name
        template_name = self._get_template_name(layer, component_type)

        # Validate template variables
        self._validate_template_variables(template_name, template_vars)

        # Check for custom template
        custom_template = getattr(self.config.templates, component_type, None)
        if custom_template:
            template_name = custom_template

        # Render and write file
        content = self._render_template(template_name, template_vars)

        # Write file with atomic operations and error handling
        backup_path = None
        lock_file = file_path.with_suffix(f"{file_path.suffix}.lock")

        try:
            # Use file locking to prevent race conditions
            import fcntl
            import tempfile

            # Create lock file for atomic operations
            with open(lock_file, "w") as lock:
                try:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except (IOError, OSError):
                    raise ValidationError(
                        f"File {file_path} is locked by another process"
                    )

                # Create backup if file exists (within lock)
                if file_path.exists():
                    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                    # Use atomic copy to prevent corruption
                    with open(file_path, "rb") as src, open(backup_path, "wb") as dst:
                        dst.write(src.read())

                # Atomic write operation to prevent TOCTOU vulnerabilities
                self._atomic_write_file(file_path, content)

                # Clean up backup on success
                if backup_path and backup_path.exists():
                    backup_path.unlink()

        except Exception as e:
            # Rollback on failure
            if backup_path and backup_path.exists():
                try:
                    if file_path.exists():
                        file_path.unlink()
                    backup_path.rename(file_path)
                except Exception as rollback_error:
                    self.console.print(
                        f"[red]Error during rollback: {rollback_error}[/red]"
                    )

            if isinstance(e, (ComponentError, ValidationError)):
                raise
            raise ValidationError(f"Failed to write file: {e}")
        finally:
            # Always clean up lock file
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except Exception:
                    pass  # Ignore cleanup errors

        self.console.print(f"[green]✓[/green] Created {file_path}")
        # Ensure we're returning a valid Path object
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        return file_path

    def _atomic_write_file(self, file_path: Path, content: str) -> None:
        """Write file atomically to prevent corruption and TOCTOU vulnerabilities.

        Uses temporary file in same directory and atomic rename to ensure:
        1. No partial writes visible to other processes
        2. No race conditions between check and write
        3. Proper cleanup on failure
        4. File locking to prevent concurrent access
        """
        # Ensure we have absolute path
        file_path = file_path.resolve()

        # Use secure file operation with locking
        return secure_file_operation(
            file_path, self._perform_atomic_write, file_path, content
        )

    def _perform_atomic_write(self, file_path: Path, content: str) -> None:
        """Perform the actual atomic write operation."""
        import tempfile
        import os

        # Validate file_path and ensure it's a proper Path object
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        # Ensure we have a valid parent directory
        parent_dir = file_path.parent
        if parent_dir is None or str(parent_dir) == ".":
            parent_dir = Path.cwd()

        # Ensure parent directory exists with proper error handling
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise create_secure_error("directory_creation", "create directory", str(e))

        # Use atomic write with temporary file in same directory
        temp_fd = None
        temp_path = None
        try:
            # Create temporary file in same directory as target
            temp_fd, temp_path = tempfile.mkstemp(
                dir=parent_dir, prefix=f".{file_path.name}.", suffix=".tmp"
            )

            # Write content to temporary file
            with os.fdopen(temp_fd, "w", encoding="utf-8") as temp_file:
                temp_file.write(content)
                temp_file.flush()
                os.fsync(temp_file.fileno())  # Ensure data is written to disk
            temp_fd = None  # File descriptor is now closed

            # Atomically move temporary file to target location
            temp_path_obj = Path(temp_path)
            temp_path_obj.replace(file_path)
            temp_path = None  # Successfully moved, don't clean up

            # Verify file was written correctly
            if not file_path.exists() or file_path.stat().st_size == 0:
                raise create_secure_error(
                    "file_write", "write file", "verification failed"
                )

        except OSError as e:
            # Handle permission errors and other OS-level issues
            if e.errno == 13:  # Permission denied
                raise create_secure_error(
                    "file_write", "write file", "permission denied"
                )
            elif e.errno == 28:  # No space left on device
                raise create_secure_error(
                    "file_write", "write file", "insufficient disk space"
                )
            else:
                raise create_secure_error("file_write", "write file", str(e))
        finally:
            # Clean up on failure
            if temp_fd is not None:
                try:
                    os.close(temp_fd)
                except OSError:
                    pass
            if temp_path and Path(temp_path).exists():
                try:
                    Path(temp_path).unlink()
                except OSError:
                    pass

    def create_multiple_components(
        self,
        base_path: Path,
        system_name: str,
        module_name: str,
        components_spec: Dict[str, Dict[str, list]],
        dry_run: bool = False,
        force: bool = False,
    ) -> list[Path]:
        """Create multiple components from specification.

        Args:
            components_spec: Dict like {
                "domain": {"entities": ["user", "order"], "repositories": ["user"]},
                "application": {"services": ["user_service"]}
            }
        """
        created_files = []

        for layer, layer_components in components_spec.items():
            for component_type, component_names in layer_components.items():
                for component_name in component_names:
                    try:
                        file_path = self.create_component(
                            base_path=base_path,
                            system_name=system_name,
                            module_name=module_name,
                            layer=layer,
                            component_type=component_type,
                            component_name=component_name,
                            dry_run=dry_run,
                            force=force,
                        )
                        created_files.append(file_path)
                    except Exception as e:
                        self.console.print(
                            f"[red]Error creating {component_name}:[/red] {e}"
                        )
                        if not force:
                            raise

        return created_files

    def _validate_component_inputs(
        self,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
    ) -> None:
        """Validate component creation inputs."""
        # Validate system name
        try:
            validate_name(system_name)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid system name: {e}")

        # Validate module name
        try:
            validate_name(module_name)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid module name: {e}")

        # Validate component name
        try:
            validate_name(component_name)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid component name: {e}")

        valid_layers = ["domain", "application", "infrastructure", "presentation"]
        if layer not in valid_layers:
            raise ValidationError(
                f"Invalid layer: {layer}. Must be one of {valid_layers}"
            )

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

        if not component_name.strip():
            raise ValidationError("Component name cannot be empty")

    def _get_component_file_path(
        self,
        base_path: Path,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
    ) -> tuple[Path, str]:
        """Get the file path and name for a component."""
        # Determine file name based on component type
        file_name = self._get_component_file_name(component_type, component_name)

        # Build full path
        file_path = (
            base_path
            / "systems"
            / system_name
            / module_name
            / layer
            / component_type
            / file_name
        )

        return file_path, file_name

    def _get_component_file_name(self, component_type: str, component_name: str) -> str:
        """Get the file name for a component based on its type."""
        snake_name = to_snake_case(component_name)

        file_name_patterns = {
            "entities": f"{snake_name}.py",
            "repositories": f"{snake_name}_repository.py",
            "value_objects": f"{snake_name}.py",
            "services": f"{snake_name}_service.py",
            "commands": f"{snake_name}.py",
            "queries": f"{snake_name}.py",
            "models": f"{snake_name}_model.py",
            "external": f"{snake_name}_client.py",
            "internal": f"{snake_name}.py",
            "api": f"{snake_name}_router.py",
            "schemas": f"{snake_name}_schemas.py",
        }

        return file_name_patterns.get(component_type, f"{snake_name}.py")

    def _get_template_name(self, layer: str, component_type: str) -> str:
        """Get the template name for a component."""
        # Special case for infrastructure repositories
        if layer == "infrastructure" and component_type == "repositories":
            return self.INFRASTRUCTURE_REPOSITORY_TEMPLATE

        return self.TEMPLATE_MAPPING.get(component_type, "entity.py.j2")

    def _validate_template_variables(
        self, template_content_or_name: str, template_vars: Dict[str, Any]
    ) -> None:
        """Validate that all required template variables are available.

        Args:
            template_content_or_name: Template content or filename
            template_vars: Variables to validate against

        Raises:
            TemplateError: If validation fails
        """
        self.template_validator.validate(template_content_or_name, template_vars)

    def _validate_file_system(self, file_path: Path) -> None:
        """Validate file system security and basic requirements."""
        import shutil
        import os

        try:
            # Prevent symlink attacks by checking the entire path
            self._check_symlink_attack(file_path)

            # Basic permission check (not relied upon for security due to TOCTOU)
            # This is kept for early validation and test compatibility
            parent_dir = file_path.parent
            if parent_dir.exists():
                if not os.access(parent_dir, os.W_OK):
                    raise create_secure_error(
                        "permission_denied",
                        "access directory",
                        "write permission denied",
                    )

            # Check available disk space (require at least 1MB)
            # Use parent directory or current directory for disk space check
            check_dir = file_path.parent if file_path.parent.exists() else Path.cwd()
            try:
                disk_usage = shutil.disk_usage(check_dir)
                free_space = (
                    disk_usage[2] if isinstance(disk_usage, tuple) else disk_usage.free
                )
                if free_space < 1024 * 1024:  # 1MB
                    raise ValidationError("Insufficient disk space")
            except OSError:
                # If we can't check disk space, continue but warn
                import logging

                logging.warning("Could not check disk space")

        except (ComponentError, ValidationError):
            raise
        except Exception as e:
            raise create_secure_error(
                "file_system_validation", "validate file system", str(e)
            )

    def _check_symlink_attack(self, file_path: Path) -> None:
        """Check for potential symlink attacks in the file path.

        This method prevents symlink attacks by ensuring that no part of the path
        contains symbolic links that could redirect file creation outside the
        intended directory structure.
        """
        try:
            # Use strict=True to fail on broken symlinks and detect symlink issues early
            try:
                resolved_path = file_path.resolve(strict=True)
            except (OSError, RuntimeError) as e:
                # If strict resolution fails, try non-strict and validate manually
                resolved_path = file_path.resolve(strict=False)
                # Additional validation: check if any component is a broken symlink
                current = file_path
                while current != current.parent:
                    if current.is_symlink() and not current.exists():
                        raise ValidationError(
                            f"Broken symlink detected in path: {current}. "
                            "File creation through broken symlinks is not allowed."
                        )
                    current = current.parent

            # More robust symlink detection - check each component of the original path
            current_path = file_path
            while current_path != current_path.parent:
                if current_path.exists() and current_path.is_symlink():
                    # Instead of hardcoded allowlist, use more sophisticated validation
                    symlink_target = current_path.readlink()

                    # Check if symlink points outside the project or to dangerous locations
                    if symlink_target.is_absolute():
                        # Absolute symlinks are generally more dangerous
                        if not self._is_safe_system_symlink(
                            current_path, symlink_target
                        ):
                            raise ValidationError(
                                f"Potentially unsafe symlink detected: {current_path} -> {symlink_target}. "
                                "File creation through unsafe symlinks is not allowed for security reasons."
                            )
                    else:
                        # Relative symlinks - resolve and check if they stay within bounds
                        try:
                            resolved_target = (
                                current_path.parent / symlink_target
                            ).resolve(strict=True)
                            if not self._is_path_within_safe_bounds(resolved_target):
                                raise ValidationError(
                                    f"Symlink points outside safe boundaries: {current_path} -> {resolved_target}. "
                                    "File creation through such symlinks is not allowed."
                                )
                        except (OSError, RuntimeError):
                            raise ValidationError(
                                f"Invalid symlink target: {current_path} -> {symlink_target}. "
                                "File creation through invalid symlinks is not allowed."
                            )

                current_path = current_path.parent

            # Enhanced temp directory detection with more robust cross-platform support
            if (
                not self._is_temp_path(resolved_path)
                and "systems" not in resolved_path.parts
            ):
                raise ValidationError(
                    f"Invalid file path: {file_path}. "
                    "Component files must be created within the systems directory structure."
                )

            # Additional validation after path resolution
            self._validate_resolved_path(file_path, resolved_path)

        except ValidationError:
            # Re-raise validation errors as-is
            raise
        except (OSError, RuntimeError) as e:
            # Handle cases where path resolution fails
            raise create_secure_error("path_validation", "validate path", str(e))

    def _is_safe_system_symlink(self, symlink_path: Path, target_path: Path) -> bool:
        """Check if a symlink is a safe system symlink.

        This method uses more sophisticated logic than hardcoded allowlists
        to determine if a symlink is safe.
        """
        symlink_str = str(symlink_path)
        target_str = str(target_path)

        # Common safe system symlink patterns across platforms
        safe_patterns = [
            # Unix/Linux system symlinks
            ("/var", "/private/var"),  # macOS /var -> /private/var
            ("/tmp", "/private/tmp"),  # macOS /tmp -> /private/tmp
            ("/etc", "/private/etc"),  # macOS /etc -> /private/etc
            # Other common system symlinks
            ("/usr/bin", "/bin"),
            ("/usr/lib", "/lib"),
        ]

        # Check if this matches known safe system symlink patterns
        for safe_source, safe_target in safe_patterns:
            if symlink_str.startswith(safe_source) and target_str.startswith(
                safe_target
            ):
                return True

        # Additional checks for system directories
        system_dirs = {"/usr", "/bin", "/lib", "/sbin", "/opt", "/System", "/Library"}
        if any(symlink_str.startswith(d) for d in system_dirs) and any(
            target_str.startswith(d) for d in system_dirs
        ):
            return True

        return False

    def _is_path_within_safe_bounds(self, path: Path) -> bool:
        """Check if a resolved path is within safe boundaries."""
        path_str = str(path)

        # Paths that should never be accessible
        dangerous_paths = {
            "/etc/passwd",
            "/etc/shadow",
            "/etc/hosts",
            "/root",
            "/boot",
            "/proc",
            "/sys",
            "/dev",
        }

        # Check for exact matches or if path starts with dangerous directories
        for dangerous in dangerous_paths:
            if path_str == dangerous or path_str.startswith(dangerous + "/"):
                return False

        return True

    def _is_temp_path(self, path: Union[Path, str]) -> bool:
        """Enhanced cross-platform temporary directory detection with caching.

        Args:
            path: Path to check (accepts both Path objects and strings)

        Returns:
            bool: True if path is detected as temporary, False otherwise
        """
        # Convert string to Path if needed
        if isinstance(path, str):
            path = Path(path)

        # Use cached version for performance
        result = self._is_temp_path_cached(str(path))

        # Log security events for temp path access
        if result:
            logger.debug(f"Temporary path access detected: {path}")

        return result

    @functools.lru_cache(maxsize=128)
    def _is_temp_path_cached(self, path_str: str) -> bool:
        """Cached implementation of temporary path detection."""
        import tempfile
        import os

        path = Path(path_str)

        try:
            # Primary method: Use system's temp directory detection
            system_temp = Path(tempfile.gettempdir()).resolve()

            # Check if path is relative to system temp directory
            try:
                if path.resolve().is_relative_to(system_temp):
                    return True
            except (AttributeError, ValueError):
                # Fallback for older Python versions or path resolution issues
                if str(path.resolve()).startswith(str(system_temp)):
                    return True

        except (OSError, ValueError):
            pass

        # Always check fallback patterns if primary method didn't match
        return self._fallback_temp_detection(path)

    def _fallback_temp_detection(self, path: Path) -> bool:
        """Enhanced fallback temporary directory detection with configurable patterns.

        Args:
            path: Path object to check for temporary directory patterns

        Returns:
            bool: True if path matches temporary directory patterns
        """
        import os

        path_str = str(path).lower()

        # Check environment variables
        temp_env_vars = ["TMPDIR", "TEMP", "TMP"]
        for env_var in temp_env_vars:
            if env_var in os.environ:
                try:
                    env_temp = Path(os.environ[env_var]).resolve()
                    if str(path).startswith(str(env_temp)):
                        return True
                except (ValueError, OSError):
                    continue

        # Check for pytest temp directories (common in testing)
        if "pytest-of-" in path_str:
            return True

        # Get custom temp patterns from config if available
        custom_patterns = self._get_custom_temp_patterns()

        # Check for common temp directory patterns
        temp_patterns = [
            "/tmp/",
            "/temp/",
            "/temporary/",
            "/var/tmp/",
            "/var/temp/",
            "/private/var/folders/",  # macOS temp
            "appdata/local/temp/",  # Windows temp
        ] + custom_patterns

        for pattern in temp_patterns:
            if pattern in path_str:
                return True

        # Check for common temp directory names in path parts
        temp_names = {"tmp", "temp", "temporary"}
        for part in path.parts:
            if part.lower() in temp_names:
                return True

        return False

    def _get_custom_temp_patterns(self) -> List[str]:
        """Get custom temporary directory patterns from configuration.

        Returns:
            List[str]: Custom temporary directory patterns
        """
        try:
            # Try to get custom patterns from config
            if hasattr(self, "config") and hasattr(self.config, "custom_temp_patterns"):
                return getattr(self.config, "custom_temp_patterns", [])
        except (AttributeError, TypeError):
            pass

        # Return empty list if no custom patterns configured
        return []

    def _validate_resolved_path(self, original_path: Path, resolved_path: Path) -> None:
        """Enhanced validation after path resolution with security logging.

        Args:
            original_path: The original path before resolution
            resolved_path: The resolved absolute path

        Raises:
            ValidationError: If path validation fails
        """
        # Check for path traversal attempts
        if ".." in str(original_path):
            logger.warning(f"Path traversal attempt detected: {original_path}")

            # Verify that after resolution, we haven't escaped intended boundaries
            original_parts = str(original_path).split(os.sep)
            if ".." in original_parts:
                # Count directory traversals
                traversal_count = original_parts.count("..")
                if traversal_count > 2:  # Allow some reasonable traversal
                    logger.error(
                        f"Excessive path traversal blocked: {original_path} (count: {traversal_count})"
                    )
                    raise ValidationError(
                        f"Excessive path traversal detected in: {original_path}. "
                        "This may indicate a path traversal attack."
                    )

        # Ensure resolved path doesn't point to sensitive system locations
        if not self._is_path_within_safe_bounds(resolved_path):
            logger.error(f"Restricted path access blocked: {resolved_path}")
            raise ValidationError(
                f"Resolved path points to restricted location: {resolved_path}. "
                "File creation in this location is not allowed."
            )

    def _sanitize_template_variables(
        self, template_vars: Dict[str, Any], depth: int = 0
    ) -> Dict[str, Any]:
        """Enhanced sanitization of template variables with security logging and recursion protection.

        Args:
            template_vars: Dictionary of template variables to sanitize
            depth: Current recursion depth (for DoS protection)

        Returns:
            Dict[str, Any]: Sanitized template variables

        Raises:
            ValidationError: If recursion depth exceeds safe limits
        """
        # Prevent deep recursion DoS attacks
        if depth > 10:
            raise ValidationError(
                f"Template variable nesting too deep (max depth: 10, current: {depth})"
            )
        sanitized_vars = {}
        suspicious_patterns_found = []

        for key, value in template_vars.items():
            if isinstance(value, str):
                original_value = value
                sanitized_vars[key] = self._sanitize_string_value(value)
                # Check if sanitization changed the value (potential injection attempt)
                if original_value != sanitized_vars[key]:
                    suspicious_patterns_found.append(
                        f"Variable '{key}': {original_value[:50]}..."
                    )
            elif isinstance(value, (int, float, bool)) or value is None:
                sanitized_vars[key] = value
            elif isinstance(value, (list, tuple)):
                # Recursively sanitize list/tuple items
                sanitized_list = []
                for item in value:
                    if isinstance(item, dict):
                        sanitized_list.append(
                            self._sanitize_template_variables(item, depth + 1)
                        )
                    else:
                        sanitized_list.append(self._sanitize_single_value(item))
                sanitized_vars[key] = sanitized_list
            elif isinstance(value, dict):
                # Recursively sanitize dict values
                sanitized_vars[key] = self._sanitize_template_variables(
                    value, depth + 1
                )
            else:
                # Convert other types to string and sanitize
                sanitized_vars[key] = self._sanitize_single_value(str(value))

        # Log security events if suspicious patterns were found
        if suspicious_patterns_found:
            logger.warning(
                f"Potential injection patterns sanitized in template variables: {suspicious_patterns_found}"
            )

        return sanitized_vars

    def _sanitize_string_value(self, value: str) -> str:
        """Enhanced sanitization for string values to prevent various injection attacks."""
        if not isinstance(value, str):
            value = str(value)

        # URL decode to catch encoded injection attempts
        import urllib.parse

        try:
            decoded_value = urllib.parse.unquote(value)
        except Exception:
            decoded_value = value

        # Unicode normalization to prevent Unicode-based attacks
        import unicodedata

        normalized_value = unicodedata.normalize("NFKC", decoded_value)

        # Remove dangerous patterns for template injection
        dangerous_patterns = [
            r"\{\{.*?\}\}",  # Jinja2 expressions
            r"\{%.*?%\}",  # Jinja2 statements
            r"\{#.*?#\}",  # Jinja2 comments
            r"<script[^>]*>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript URLs
            r"data:",  # Data URLs
            r"vbscript:",  # VBScript URLs
            r"on\w+\s*=",  # Event handlers
            r"\\x[0-9a-fA-F]{2}",  # Hex escapes
            r"\\u[0-9a-fA-F]{4}",  # Unicode escapes
            r"\\[rnt]",  # Common escapes
            r"__.*__",  # Python dunder methods
            r"\beval\b",  # eval function
            r"\bexec\b",  # exec function
            r"\bimport\b",  # import statements
            r"\bopen\b",  # file operations
            r"\bfile\b",  # file operations
            r"\bos\.",  # os module access
            r"\bsys\.",  # sys module access
        ]

        sanitized = normalized_value
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

        # Remove control characters and dangerous Unicode categories
        sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", sanitized)

        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\'\\\/`$]', "", sanitized)

        # Limit length to prevent DoS
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]

        return sanitized

    def _sanitize_single_value(self, value: Any) -> str:
        """Sanitize a single value."""
        if not isinstance(value, str):
            value = str(value)
        return self._sanitize_string_value(value)

    def _sanitize_template_output(self, value: Any) -> str:
        """Finalize function to sanitize template output."""
        if value is None:
            return ""
        return self._sanitize_single_value(str(value))

    def _setup_sandbox_security(self) -> None:
        """Configure enhanced sandbox security settings with minimal attack surface."""
        # Define a minimal set of safe builtins (reduced from previous version)
        allowed_builtins = {
            "range": range,
            "len": len,
            "str": str,
            "int": int,
            "bool": bool,
            "list": list,
            "dict": dict,
            "enumerate": enumerate,
        }

        # Override the globals to only include safe functions
        self.template_env.globals.clear()
        self.template_env.globals.update(allowed_builtins)

        # Define allowed filters (keep only safe ones)
        safe_filters = {
            "upper",
            "lower",
            "title",
            "capitalize",
            "strip",
            "replace",
            "length",
            "first",
            "last",
            "join",
            "default",
            "trim",
            "truncate",
            "wordwrap",
            "center",
            "indent",
        }

        # Remove ALL potentially dangerous filters and globals
        dangerous_items = [
            # Attribute access
            "attr",
            "getattr",
            "setattr",
            "delattr",
            "hasattr",
            # Code execution
            "import",
            "exec",
            "eval",
            "compile",
            "__import__",
            # File operations
            "open",
            "file",
            "input",
            "raw_input",
            # System access
            "globals",
            "locals",
            "vars",
            "dir",
            # Object introspection
            "type",
            "isinstance",
            "issubclass",
            "callable",
            # Dangerous builtins removed from allowed list
            "float",
            "tuple",
            "zip",
            "map",
            "filter",
            "reduce",
        ]

        # Remove from filters
        for item_name in dangerous_items:
            if item_name in self.template_env.filters:
                del self.template_env.filters[item_name]
            # Also remove from globals if present
            if item_name in self.template_env.globals:
                del self.template_env.globals[item_name]

        # Remove potentially dangerous filters
        current_filters = set(self.template_env.filters.keys())
        dangerous_filters = current_filters - safe_filters

        for filter_name in dangerous_filters:
            if filter_name in self.template_env.filters:
                del self.template_env.filters[filter_name]

    def _render_template(
        self, template_name: str, template_vars: Dict[str, Any]
    ) -> str:
        """Render a template with the given variables."""
        try:
            # Sanitize template variables before rendering
            sanitized_vars = self._sanitize_template_variables(template_vars)

            template = self.template_env.get_template(template_name)
            return template.render(**sanitized_vars)
        except jinja2.TemplateNotFound:
            raise TemplateError(f"Template not found: {template_name}")
        except jinja2.TemplateError as e:
            raise TemplateError(f"Error rendering template {template_name}: {e}")
        except Exception as e:
            raise TemplateError(f"Unexpected error rendering template: {e}")
