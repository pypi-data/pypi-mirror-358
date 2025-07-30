"""Tests for the generator factory and dependency injection patterns."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from rich.console import Console

from fast_clean_architecture.config import Config
from fast_clean_architecture.exceptions import ValidationError
from fast_clean_architecture.generators import (
    ComponentGenerator,
    ConfigUpdater,
    PackageGenerator,
)
from fast_clean_architecture.generators.generator_factory import (
    DependencyContainer,
    GeneratorFactory,
    create_generator_factory,
)
from fast_clean_architecture.protocols import (
    SecurePathHandler,
    TemplateValidatorProtocol,
)


class TestDependencyContainer:
    """Test the dependency container functionality."""

    def test_dependency_container_initialization(self, sample_config: Config) -> None:
        """Test that dependency container initializes correctly."""
        console = Console()
        container = DependencyContainer(sample_config, console)

        assert container.config == sample_config
        assert container.console == console
        assert container._template_validator is None
        assert container._path_handler is None

    def test_get_template_validator(self, sample_config: Config) -> None:
        """Test template validator creation and caching."""
        container = DependencyContainer(sample_config)

        # First call should create validator
        validator1 = container.template_validator
        assert validator1 is not None

        # Second call should return same instance (cached)
        validator2 = container.template_validator
        assert validator1 is validator2

    def test_get_path_handler(self, sample_config: Config) -> None:
        """Test path handler creation and caching."""
        container = DependencyContainer(sample_config)

        # First call creates the path handler
        handler1 = container.path_handler
        assert handler1 is not None
        assert container._path_handler is handler1

        # Second call returns the same instance (cached)
        handler2 = container.path_handler
        assert handler2 is handler1


class TestGeneratorFactory:
    """Test the generator factory functionality."""

    def test_factory_initialization(self, sample_config: Config) -> None:
        """Test that factory initializes with dependency container."""
        container = DependencyContainer(sample_config)
        factory = GeneratorFactory(container)

        assert factory.dependencies == container
        assert "component" in factory._generators
        assert "package" in factory._generators
        assert "config" in factory._generators

    def test_create_component_generator(self, sample_config: Config) -> None:
        """Test creating component generator through factory."""
        container = DependencyContainer(sample_config)
        factory = GeneratorFactory(container)

        generator = factory.create_generator("component")

        assert isinstance(generator, ComponentGenerator)
        # Verify config is passed correctly (cast to ComponentGenerator)
        comp_gen = generator  # type: ComponentGenerator
        assert comp_gen.config == sample_config
        # Verify dependencies are injected
        assert comp_gen.template_validator is not None
        assert comp_gen.path_handler is not None

    def test_create_package_generator(self, sample_config: Config) -> None:
        """Test creating package generator through factory."""
        container = DependencyContainer(sample_config)
        factory = GeneratorFactory(container)

        generator = factory.create_generator("package")

        assert isinstance(generator, PackageGenerator)
        assert generator.console == container.console

    def test_create_config_updater(self, sample_config: Config, tmp_path: Path) -> None:
        """Test creating config updater through factory."""
        container = DependencyContainer(sample_config)
        factory = GeneratorFactory(container)

        config_path = tmp_path / "test_config.yaml"
        generator = factory.create_generator("config", config_path=config_path)

        assert isinstance(generator, ConfigUpdater)
        assert generator.config_path == config_path
        assert generator.console == container.console

    def test_create_config_updater_default_path(self, sample_config: Config) -> None:
        """Test creating config updater with default path."""
        container = DependencyContainer(sample_config)
        factory = GeneratorFactory(container)

        generator = factory.create_generator("config")

        assert isinstance(generator, ConfigUpdater)
        assert generator.config_path == Path("fca_config.yaml")

    def test_unsupported_generator_type(self, sample_config: Config) -> None:
        """Test error handling for unsupported generator types."""
        container = DependencyContainer(sample_config)
        factory = GeneratorFactory(container)

        with pytest.raises(ValueError, match="Unsupported generator type: invalid"):
            factory.create_generator("invalid")

    def test_get_available_types(self, sample_config: Config) -> None:
        """Test getting available generator types."""
        container = DependencyContainer(sample_config)
        factory = GeneratorFactory(container)

        types = factory.get_available_types()

        assert "component" in types
        assert "package" in types
        assert "config" in types
        assert len(types) == 3

    def test_register_custom_generator(self, sample_config: Config) -> None:
        """Test registering a custom generator type."""
        container = DependencyContainer(sample_config)
        factory = GeneratorFactory(container)

        class CustomGenerator:
            def __init__(self, **kwargs: Any) -> None:
                self.kwargs = kwargs

            # Implement GeneratorProtocol (empty base protocol)
            pass

        factory.register_generator("custom", CustomGenerator)

        assert "custom" in factory._generators
        assert "custom" in factory.get_available_types()

    def test_shared_dependencies(self, sample_config: Config) -> None:
        """Test that multiple generators share the same dependencies."""
        container = DependencyContainer(sample_config)
        factory = GeneratorFactory(container)

        gen1 = factory.create_generator("component")
        gen2 = factory.create_generator("component")

        # Verify shared dependencies (cast to ComponentGeneratorProtocol for attribute access)
        from typing import cast

        from fast_clean_architecture.generators import ComponentGeneratorProtocol

        comp_gen1 = cast(ComponentGeneratorProtocol, gen1)
        comp_gen2 = cast(ComponentGeneratorProtocol, gen2)
        assert comp_gen1.template_validator is comp_gen2.template_validator
        assert comp_gen1.path_handler is comp_gen2.path_handler


class TestCreateGeneratorFactory:
    """Test the convenience function for creating generator factories."""

    def test_create_generator_factory(self, sample_config: Config) -> None:
        """Test the convenience function creates a properly configured factory."""
        console = Console()
        factory = create_generator_factory(sample_config, console)

        assert isinstance(factory, GeneratorFactory)
        assert factory.dependencies.config == sample_config
        assert factory.dependencies.console == console

    def test_create_generator_factory_default_console(
        self, sample_config: Config
    ) -> None:
        """Test factory creation with default console."""
        factory = create_generator_factory(sample_config)

        assert isinstance(factory, GeneratorFactory)
        assert factory.dependencies.config == sample_config
        assert factory.dependencies.console is not None


class TestDependencyInjection:
    """Test dependency injection in ComponentGenerator."""

    def test_component_generator_with_injected_dependencies(
        self, sample_config: Config
    ) -> None:
        """Test ComponentGenerator with manually injected dependencies."""
        mock_validator = Mock(spec=TemplateValidatorProtocol)
        mock_path_handler = Mock(spec=SecurePathHandler)
        console = Console()

        generator = ComponentGenerator(
            config=sample_config,
            template_validator=mock_validator,
            path_handler=mock_path_handler,
            console=console,
        )

        assert generator.template_validator is mock_validator
        assert generator.path_handler is mock_path_handler
        assert generator.console is console

    def test_component_generator_with_partial_injection(
        self, sample_config: Config
    ) -> None:
        """Test ComponentGenerator with only some dependencies injected."""
        mock_validator = Mock(spec=TemplateValidatorProtocol)

        generator = ComponentGenerator(
            config=sample_config, template_validator=mock_validator
        )

        assert generator.template_validator is mock_validator
        # Path handler should be created with defaults
        assert generator.path_handler is not None
        assert isinstance(generator.path_handler, SecurePathHandler)

    def test_component_generator_backward_compatibility(
        self, sample_config: Config
    ) -> None:
        """Test that ComponentGenerator still works without dependency injection."""
        console = Console()

        # Old-style instantiation should still work
        generator = ComponentGenerator(config=sample_config, console=console)

        assert generator.config == sample_config
        assert generator.console == console
        # Dependencies should be created with defaults
        assert generator.template_validator is not None
        assert generator.path_handler is not None


class TestFactoryIntegration:
    """Integration tests for the factory pattern."""

    def test_factory_creates_working_component_generator(
        self, sample_config: Config, tmp_path: Path
    ) -> None:
        """Test that factory-created component generator works correctly."""
        factory = create_generator_factory(sample_config)
        generator = factory.create_generator("component")

        # Test that the generator can perform its basic functions
        assert hasattr(generator, "create_component")
        assert hasattr(generator, "validate_component")
        # Cast to ComponentGeneratorProtocol for attribute access
        from typing import cast

        from fast_clean_architecture.generators import ComponentGeneratorProtocol

        comp_gen = cast(ComponentGeneratorProtocol, generator)
        assert comp_gen.config == sample_config

    def test_factory_error_handling(self, sample_config: Config) -> None:
        """Test error handling in factory methods."""
        factory = create_generator_factory(sample_config)

        # Test with invalid generator type
        with pytest.raises(ValueError) as exc_info:
            factory.create_generator("nonexistent")

        assert "Unsupported generator type" in str(exc_info.value)
        assert "Available types:" in str(exc_info.value)

    def test_factory_with_custom_dependencies(self, sample_config: Config) -> None:
        """Test factory with custom dependency configuration."""
        # Create custom dependency container
        container = DependencyContainer(sample_config)

        # Override with custom path handler
        custom_path_handler: SecurePathHandler[Any] = SecurePathHandler(
            max_path_length=8192, allowed_extensions=[".py", ".j2", ".yaml"]
        )
        container._path_handler = custom_path_handler

        factory = GeneratorFactory(container)
        generator = factory.create_generator("component")

        # Verify custom path handler is used (cast to ComponentGeneratorProtocol)
        from typing import cast

        from fast_clean_architecture.generators import ComponentGeneratorProtocol

        comp_gen = cast(ComponentGeneratorProtocol, generator)
        assert comp_gen.path_handler is custom_path_handler
        assert comp_gen.path_handler.max_path_length == 8192


@pytest.fixture
def sample_config() -> Config:
    """Create a sample configuration for testing."""
    config = Config.create_default()
    config.project.name = "test_project"
    config.project.description = "Test project for factory pattern"
    return config
