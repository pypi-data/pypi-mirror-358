"""Fast Clean Architecture - CLI tool for scaffolding clean architecture in FastAPI projects."""

__version__ = "1.0.0"
__author__ = "Agoro, Adegbenga. B (IAM)"
__email__ = "adegbenga@alden-technologies.com"

from .cli import app
from .config import Config
from .exceptions import (
    ConfigurationError,
    FastCleanArchitectureError,
    FileConflictError,
    ValidationError,
)

__all__ = [
    "app",
    "Config",
    "FastCleanArchitectureError",
    "ConfigurationError",
    "ValidationError",
    "FileConflictError",
]
