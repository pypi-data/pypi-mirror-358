"""Custom exceptions for Fast Clean Architecture."""


class FastCleanArchitectureError(Exception):
    """Base exception for all Fast Clean Architecture errors."""

    pass


class ConfigurationError(FastCleanArchitectureError):
    """Raised when there's an issue with configuration."""

    pass


class ValidationError(FastCleanArchitectureError):
    """Raised when validation fails."""

    pass


class FileConflictError(FastCleanArchitectureError):
    """Raised when there's a file or directory conflict."""

    pass


class TemplateError(FastCleanArchitectureError):
    """Raised when there's an issue with template rendering."""

    pass


class TemplateValidationError(TemplateError):
    """Base class for template validation errors."""

    pass


class TemplateMissingVariablesError(TemplateValidationError):
    """Raised when required template variables are missing."""

    def __init__(self, missing_vars: set, message: str = None):
        self.missing_vars = missing_vars
        if message is None:
            message = f"Missing required template variables: {', '.join(sorted(missing_vars))}"
        super().__init__(message)


class TemplateUndefinedVariableError(TemplateValidationError):
    """Raised when template contains undefined variables during rendering."""

    def __init__(self, variable_name: str, message: str = None):
        self.variable_name = variable_name
        if message is None:
            message = f"Undefined template variable: {variable_name}"
        super().__init__(message)


class ComponentError(FastCleanArchitectureError):
    """Raised when there's an issue with component generation."""

    pass
