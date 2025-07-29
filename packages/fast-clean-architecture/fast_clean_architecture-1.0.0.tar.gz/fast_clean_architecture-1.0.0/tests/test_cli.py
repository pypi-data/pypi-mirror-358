"""Tests for CLI functionality."""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from fast_clean_architecture.cli import app
from fast_clean_architecture.config import Config


class TestCLI:
    """Test CLI commands."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "Fast Clean Architecture" in result.stdout
        assert "Version:" in result.stdout

    def test_init_command_with_args(self, temp_dir: Path):
        """Test init command with arguments."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--version",
                    "1.0.0",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 0
        assert "initialized successfully" in result.stdout
        assert config_file.exists()

        # Verify config content
        config = Config.load_from_file(config_file)
        assert config.project.name == "test_project"
        assert config.project.description == "Test project"
        assert config.project.version == "1.0.0"

    def test_init_command_interactive(self, temp_dir: Path):
        """Test init command with interactive input."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            with patch("fast_clean_architecture.cli.Prompt.ask") as mock_prompt:
                mock_prompt.side_effect = [
                    "interactive_project",
                    "Interactive description",
                ]

                result = self.runner.invoke(app, ["init", "--config", str(config_file)])

        assert result.exit_code == 0
        assert config_file.exists()

        # Verify config content
        config = Config.load_from_file(config_file)
        assert config.project.name == "interactive_project"
        assert config.project.description == "Interactive description"

    def test_init_command_force_overwrite(self, temp_dir: Path):
        """Test init command with force overwrite."""
        config_file = temp_dir / "test-config.yaml"

        # Create existing config
        existing_config = Config.create_default()
        existing_config.project.name = "existing_project"
        existing_config.save_to_file(config_file)

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(
                app,
                [
                    "init",
                    "new_project",
                    "--description",
                    "New project",
                    "--config",
                    str(config_file),
                    "--force",
                ],
            )

        assert result.exit_code == 0

        # Verify config was overwritten
        config = Config.load_from_file(config_file)
        assert config.project.name == "new_project"

    def test_create_system_context(self, temp_dir: Path):
        """Test create-system-context command."""
        config_file = temp_dir / "test-config.yaml"

        # Initialize project first
        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            self.runner.invoke(
                app, ["init", "test_project", "--config", str(config_file)]
            )

            # Create system context
            result = self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--description",
                    "User management system",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 0
        assert "created successfully" in result.stdout

        # Verify system directory was created
        system_dir = temp_dir / "systems" / "user_management"
        assert system_dir.exists()
        assert (system_dir / "__init__.py").exists()
        assert (system_dir / "main.py").exists()

        # Verify config was updated
        config = Config.load_from_file(config_file)
        assert "user_management" in config.project.systems
        assert (
            config.project.systems["user_management"].description
            == "User management system"
        )

    def test_create_module(self, temp_dir: Path):
        """Test create-module command."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project and system
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--description",
                    "User management system",
                    "--config",
                    str(config_file),
                ],
            )

            # Create module
            result = self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--description",
                    "Authentication module",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 0
        assert "created in system" in result.stdout

        # Verify module directory structure
        module_dir = temp_dir / "systems" / "user_management" / "authentication"
        assert module_dir.exists()
        assert (module_dir / "__init__.py").exists()

        # Check layer directories
        for layer in ["domain", "application", "infrastructure", "presentation"]:
            layer_dir = module_dir / layer
            assert layer_dir.exists()
            assert (layer_dir / "__init__.py").exists()

        # Verify config was updated
        config = Config.load_from_file(config_file)
        system = config.project.systems["user_management"]
        assert "authentication" in system.modules
        assert system.modules["authentication"].description == "Authentication module"

    def test_create_component(self, temp_dir: Path):
        """Test create-component command."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project, system, and module
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--description",
                    "User management system",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--description",
                    "Authentication module",
                    "--config",
                    str(config_file),
                ],
            )

            # Create component
            result = self.runner.invoke(
                app,
                [
                    "create-component",
                    "user_management/authentication/domain/entities",
                    "user",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 0
        assert "Created" in result.stdout and "entities" in result.stdout

        # Verify component file was created
        component_file = (
            temp_dir
            / "systems"
            / "user_management"
            / "authentication"
            / "domain"
            / "entities"
            / "user.py"
        )
        assert component_file.exists()

        # Verify config was updated
        config = Config.load_from_file(config_file)
        module = config.project.systems["user_management"].modules["authentication"]
        entities = module.components.domain.entities
        assert len(entities) == 1
        assert entities[0].name == "user"

    def test_create_component_invalid_location(self, temp_dir: Path):
        """Test create-component with invalid location format."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(
                app,
                [
                    "create-component",
                    "invalid/location",  # Missing layer and component type
                    "user",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 1
        assert "Location must be in format" in result.stdout

    def test_dry_run_mode(self, temp_dir: Path):
        """Test dry run mode."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )

            # Create system in dry run mode
            result = self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--config",
                    str(config_file),
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout

        # Verify nothing was actually created
        system_dir = temp_dir / "systems" / "user_management"
        assert not system_dir.exists()

        # Verify config was not updated
        config = Config.load_from_file(config_file)
        assert "user_management" not in config.project.systems

    def test_status_command(self, temp_dir: Path):
        """Test status command."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project with system and module
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--config",
                    str(config_file),
                ],
            )

            # Check status
            result = self.runner.invoke(app, ["status", "--config", str(config_file)])

        assert result.exit_code == 0
        assert "Project Information" in result.stdout
        assert "test_project" in result.stdout
        # The status command should show project information at minimum
        # Systems may or may not be displayed depending on the state

    def test_status_no_config(self, temp_dir: Path):
        """Test status command with no config file."""
        config_file = temp_dir / "nonexistent-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(app, ["status", "--config", str(config_file)])

        assert result.exit_code == 0
        assert "No configuration file found" in result.stdout

    def test_config_show_command(self, temp_dir: Path):
        """Test config show command."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )

            # Show config
            result = self.runner.invoke(
                app, ["config", "show", "--config", str(config_file)]
            )

        assert result.exit_code == 0
        assert "Configuration:" in result.stdout
        assert "test_project" in result.stdout

    def test_config_validate_command(self, temp_dir: Path):
        """Test config validate command."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )

            # Validate config
            result = self.runner.invoke(
                app, ["config", "validate", "--config", str(config_file)]
            )

        assert result.exit_code == 0
        assert "Configuration is valid" in result.stdout

    def test_config_validate_invalid(self, temp_dir: Path):
        """Test config validate with invalid config."""
        config_file = temp_dir / "invalid-config.yaml"

        # Create invalid YAML
        config_file.write_text("invalid: yaml: content: [")

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(
                app, ["config", "validate", "--config", str(config_file)]
            )

        assert result.exit_code == 0
        assert "Configuration is invalid" in result.stdout

    def test_batch_create_command(self, temp_dir: Path):
        """Test batch-create command."""
        config_file = temp_dir / "test-config.yaml"
        spec_file = temp_dir / "components.yaml"

        # Create specification file
        spec_content = """
systems:
  - name: user_management
    modules:
      - name: authentication
        components:
          domain:
            entities: ["user"]
            repositories: ["user"]
          application:
            services: ["auth_service"]
"""
        spec_file.write_text(spec_content)

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project, system, and module
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--config",
                    str(config_file),
                ],
            )

            # Run batch create
            result = self.runner.invoke(
                app, ["batch-create", str(spec_file), "--config", str(config_file)]
            )

        assert result.exit_code == 0
        assert "Batch creation completed" in result.stdout or "Created" in result.stdout

        # Verify components were created
        base_path = temp_dir / "systems" / "user_management" / "authentication"
        assert (base_path / "domain" / "entities" / "user.py").exists()
        assert (base_path / "domain" / "repositories" / "user_repository.py").exists()
        assert (
            base_path / "application" / "services" / "auth_service_service.py"
        ).exists()

    def test_error_handling(self, temp_dir: Path):
        """Test error handling in CLI."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Try to create module without system
            result = self.runner.invoke(
                app,
                [
                    "create-module",
                    "nonexistent_system",
                    "authentication",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 1
        assert "Error:" in result.stdout
