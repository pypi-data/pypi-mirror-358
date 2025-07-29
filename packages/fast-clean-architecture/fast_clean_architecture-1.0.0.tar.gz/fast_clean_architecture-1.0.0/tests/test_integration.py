"""Integration tests for the fast-clean-architecture package."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from fast_clean_architecture.cli import app
from fast_clean_architecture.config import Config
from fast_clean_architecture.exceptions import (
    ValidationError,
    FileConflictError,
    ComponentError,
    TemplateError,
    ConfigurationError,
)
from fast_clean_architecture.generators.component_generator import ComponentGenerator
from fast_clean_architecture.utils import get_template_variables


class TestIntegration:
    """Integration tests for the entire system."""

    @pytest.fixture
    def project_dir(self, tmp_path):
        """Create a temporary project directory with proper structure."""
        project_path = tmp_path / "test_project"
        project_path.mkdir()

        # Create basic project structure
        (project_path / "systems").mkdir()
        (project_path / "shared").mkdir()
        (project_path / "tests").mkdir()

        return project_path

    @pytest.fixture
    def config_file(self, project_dir):
        """Create a test configuration file."""
        config_path = project_dir / "fca-config.yaml"
        config = Config.create_default()
        config.project.name = "test_project"
        config.project.description = "A test project for integration testing"
        config.save_to_file(config_path)
        return config_path

    def test_full_component_generation_workflow(self, project_dir, config_file):
        """Test the complete workflow of generating components."""
        config = Config.load_from_file(config_file)
        generator = ComponentGenerator(config)

        # Generate entity
        entity_result = generator.create_component(
            base_path=project_dir,
            system_name="user_management",
            module_name="users",
            layer="domain",
            component_type="entities",
            component_name="user",
        )

        assert entity_result.exists()
        assert "class User" in entity_result.read_text()

        # Generate repository
        repo_result = generator.create_component(
            base_path=project_dir,
            system_name="user_management",
            module_name="users",
            layer="infrastructure",
            component_type="repositories",
            component_name="user",
        )

        assert repo_result.exists()
        repo_content = repo_result.read_text()
        assert "SQLAlchemy" in repo_content and "Repository" in repo_content

        # Generate service
        service_result = generator.create_component(
            base_path=project_dir,
            system_name="user_management",
            module_name="users",
            layer="application",
            component_type="services",
            component_name="user",
        )

        assert service_result.exists()
        assert "class UserService" in service_result.read_text()

        # Verify directory structure
        expected_structure = [
            "systems/user_management/users/domain/entities/user.py",
            "systems/user_management/users/infrastructure/repositories/user_repository.py",
            "systems/user_management/users/application/services/user_service.py",
        ]

        for expected_path in expected_structure:
            full_path = project_dir / expected_path
            assert full_path.exists(), f"Expected file not found: {expected_path}"

    def test_multiple_systems_generation(self, project_dir, config_file):
        """Test generating components across multiple systems."""
        config = Config.load_from_file(config_file)
        generator = ComponentGenerator(config)

        systems = [
            ("user_management", "users", "user"),
            ("order_management", "orders", "order"),
            ("inventory_management", "products", "product"),
        ]

        for system_name, module_name, component_name in systems:
            # Generate entity for each system
            result = generator.create_component(
                base_path=project_dir,
                system_name=system_name,
                module_name=module_name,
                layer="domain",
                component_type="entities",
                component_name=component_name,
            )

            assert result.exists()

            # Verify content
            content = result.read_text()
            expected_class = f"class {component_name.title()}"
            assert expected_class in content

        # Verify all systems were created
        systems_dir = project_dir / "systems"
        created_systems = [d.name for d in systems_dir.iterdir() if d.is_dir()]
        expected_systems = [
            "user_management",
            "order_management",
            "inventory_management",
        ]

        for expected_system in expected_systems:
            assert expected_system in created_systems

    def test_config_backup_and_restore(self, project_dir):
        """Test configuration backup and restore functionality."""
        config_path = project_dir / "fca-config.yaml"

        # Create initial config
        config = Config.create_default()
        config.project.name = "original_project"
        config.save_to_file(config_path)

        # Modify config (should create backup)
        config.project.name = "modified_project"
        config.project.description = "Modified description"
        config.save_to_file(config_path)

        # Verify backup was created
        backup_files = list(project_dir.glob("fca-config.yaml.backup.*"))
        assert len(backup_files) >= 1

        # Verify current config has new values
        current_config = Config.load_from_file(config_path)
        assert current_config.project.name == "modified_project"
        assert current_config.project.description == "Modified description"

        # Verify backup has original values
        backup_config = Config.load_from_file(backup_files[0])
        assert backup_config.project.name == "original_project"

    def test_template_variables_consistency(self, project_dir, config_file):
        """Test that template variables are consistent across components."""
        config = Config.load_from_file(config_file)
        generator = ComponentGenerator(config)

        # Generate components
        components = [
            ("entities", "user"),
            ("repositories", "user"),
            ("services", "user"),
        ]

        generated_files = []
        for component_type, component_name in components:
            result = generator.create_component(
                base_path=project_dir,
                system_name="test_system",
                module_name="test_module",
                layer=(
                    "domain"
                    if component_type in ["entities", "repositories"]
                    else "application"
                ),
                component_type=component_type,
                component_name=component_name,
            )
            assert result.exists()
            generated_files.append(result)

        # Verify consistent naming across files
        for file_path in generated_files:
            content = file_path.read_text()

            # Check for proper imports and class names
            if "entities" in str(file_path):
                assert "class User" in content
                assert (
                    "test_module" in content.lower()
                )  # Only entity template uses module_name
            elif "repositories" in str(file_path):
                assert "class UserRepository" in content or "SQLAlchemy" in content
            elif "services" in str(file_path):
                assert "class UserService" in content

    def test_error_handling_integration(self, project_dir, config_file):
        """Test error handling across the entire system."""
        config = Config.load_from_file(config_file)
        generator = ComponentGenerator(config)

        # Test invalid component type
        with pytest.raises((ComponentError, ValidationError, TemplateError)):
            generator.create_component(
                base_path=project_dir,
                system_name="test_system",
                module_name="test_module",
                layer="domain",
                component_type="nonexistent_component_type",
                component_name="test",
            )

        # Test invalid component name
        with pytest.raises((ComponentError, ValidationError)):
            generator.create_component(
                base_path=project_dir,
                system_name="test_system",
                module_name="test_module",
                layer="domain",
                component_type="entities",
                component_name="123invalid",
            )

    def test_dry_run_mode(self, project_dir, config_file):
        """Test dry run mode functionality."""
        config = Config.load_from_file(config_file)
        generator = ComponentGenerator(config)

        # Perform dry run
        result = generator.create_component(
            base_path=project_dir,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="entities",
            component_name="user",
            dry_run=True,
        )

        assert not result.exists()  # File should not be created in dry run

        # Verify the path that would be created
        expected_path = (
            project_dir
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "entities"
            / "user.py"
        )
        assert result == expected_path

    def test_force_overwrite_functionality(self, project_dir, config_file):
        """Test force overwrite functionality."""
        config = Config.load_from_file(config_file)
        generator = ComponentGenerator(config)

        # Create initial component
        result1 = generator.create_component(
            base_path=project_dir,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="entities",
            component_name="user",
        )

        assert result1.exists()
        original_content = result1.read_text()

        # Modify the file
        result1.write_text(original_content + "\n# Modified content")
        modified_content = result1.read_text()

        # Try to generate again without force (should fail)
        with pytest.raises(FileConflictError):
            generator.create_component(
                base_path=project_dir,
                system_name="test_system",
                module_name="test_module",
                layer="domain",
                component_type="entities",
                component_name="user",
                force=False,
            )

        assert result1.read_text() == modified_content  # File unchanged

        # Generate again with force (should succeed)
        result3 = generator.create_component(
            base_path=project_dir,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="entities",
            component_name="user",
            force=True,
        )

        assert result3.exists()
        new_content = result3.read_text()
        assert "# Modified content" not in new_content  # File was overwritten

    def test_template_variable_generation(self):
        """Test template variable generation for different scenarios."""
        # Test basic variables
        variables = get_template_variables(
            system_name="user_management",
            module_name="users",
            component_name="user_profile",
            component_type="entities",
        )

        # Verify naming conventions
        assert variables["component_name"] == "user_profile"
        assert variables["ComponentName"] == "UserProfile"
        assert variables["component_name_camel"] == "userProfile"

        # Verify system and module names
        assert variables["system_name"] == "user_management"
        assert variables["module_name"] == "users"

        # Verify file names
        assert variables["entity_file"] == "user_profile.py"
        assert variables["repository_file"] == "user_profile_repository.py"
        assert variables["service_file"] == "user_profile_service.py"

        # Verify metadata
        assert "generated_at" in variables
        assert "generator_version" in variables

        # Verify import paths
        assert "domain_import_path" in variables
        assert "application_import_path" in variables
        assert "infrastructure_import_path" in variables

    def test_concurrent_generation(self, project_dir, config_file):
        """Test concurrent component generation."""
        import threading
        import time

        config = Config.load_from_file(config_file)
        generator = ComponentGenerator(config)
        results = []
        errors = []

        def generate_component(system_name, module_name, component_name):
            try:
                result = generator.create_component(
                    base_path=project_dir,
                    system_name=system_name,
                    module_name=module_name,
                    layer="domain",
                    component_type="entities",
                    component_name=component_name,
                )
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads to generate components concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=generate_component,
                args=(f"system_{i}", f"module_{i}", f"component_{i}"),
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify results
        assert (
            len(errors) == 0
        ), f"Errors occurred during concurrent generation: {errors}"
        assert len(results) == 5

        for result in results:
            assert result.exists()

    def test_large_project_structure(self, project_dir, config_file):
        """Test generation in a large project structure."""
        config = Config.load_from_file(config_file)
        generator = ComponentGenerator(config)

        # Generate a large number of components
        systems = [f"system_{i}" for i in range(10)]
        modules = [f"module_{j}" for j in range(5)]
        components = [f"component_{k}" for k in range(3)]

        generated_count = 0
        for system in systems:
            for module in modules:
                for component in components:
                    result = generator.create_component(
                        base_path=project_dir,
                        system_name=system,
                        module_name=module,
                        layer="domain",
                        component_type="entities",
                        component_name=component,
                    )

                    assert result.exists()
                    generated_count += 1

        # Verify total count
        expected_count = len(systems) * len(modules) * len(components)
        assert generated_count == expected_count

        # Verify directory structure
        systems_dir = project_dir / "systems"
        created_systems = [d.name for d in systems_dir.iterdir() if d.is_dir()]
        assert len(created_systems) == len(systems)

    def test_configuration_validation_integration(self, project_dir):
        """Test configuration validation in integration scenarios."""
        config_path = project_dir / "fca-config.yaml"

        # Create invalid YAML configuration
        invalid_yaml = "invalid: yaml: content: ["

        with open(config_path, "w") as f:
            f.write(invalid_yaml)

        # Attempt to load invalid configuration
        with pytest.raises(ConfigurationError):  # Should raise configuration error
            Config.load_from_file(config_path)

    def test_cleanup_and_rollback(self, project_dir, config_file):
        """Test cleanup and rollback functionality."""
        config = Config.load_from_file(config_file)
        generator = ComponentGenerator(config)

        # Mock a failure during file writing in the atomic write operation
        with patch("tempfile.mkstemp", side_effect=OSError("Disk full")):
            with pytest.raises(ValidationError, match="Failed to write file"):
                generator.create_component(
                    base_path=project_dir,
                    system_name="test_system",
                    module_name="test_module",
                    layer="domain",
                    component_type="entities",
                    component_name="user",
                )

        # Verify no partial files were left behind
        expected_path = (
            project_dir
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "entities"
            / "user.py"
        )
        assert not expected_path.exists()

    def test_end_to_end_workflow(self, project_dir):
        """Test complete end-to-end workflow."""
        # 1. Create configuration
        config = Config.create_default()
        config.project.name = "e2e_test_project"
        config.project.description = "End-to-end test project"
        config_path = project_dir / "fca-config.yaml"
        config.save_to_file(config_path)

        # 2. Initialize generator
        generator = ComponentGenerator(config)

        # 3. Generate complete system
        system_name = "user_management"
        module_name = "users"
        component_name = "user"

        # Generate all component types
        component_types = ["entities", "repositories", "services"]
        generated_files = []

        for component_type in component_types:
            file_path = generator.create_component(
                base_path=project_dir,
                system_name=system_name,
                module_name=module_name,
                layer=(
                    "domain"
                    if component_type == "entities"
                    else (
                        "application"
                        if component_type == "services"
                        else "infrastructure"
                    )
                ),
                component_type=component_type,
                component_name=component_name,
            )

            assert file_path.exists()
            generated_files.append(file_path)

        # 4. Verify generated content
        for file_path in generated_files:
            content = file_path.read_text()

            # Verify metadata (only for entities and services)
            if "entities" in str(file_path) or "services" in str(file_path):
                assert "Generated at:" in content
                assert "Generator version:" in content

            # Verify imports and structure
            assert "from typing import" in content

            # Verify proper class definitions
            if "entities" in str(file_path):
                assert "@dataclass" in content
                assert "class User:" in content
                assert "from datetime import datetime" in content
            elif "repositories" in str(file_path):
                assert "SQLAlchemy" in content and "Repository" in content
                assert "def get_by_id" in content
                assert "from sqlalchemy.orm import Session" in content
            elif "services" in str(file_path):
                assert "class UserService:" in content
                assert "def __init__" in content

        # 5. Verify project structure
        expected_structure = [
            "fca-config.yaml",
            "systems/user_management/users/domain/entities/user.py",
            "systems/user_management/users/infrastructure/repositories/user_repository.py",
            "systems/user_management/users/application/services/user_service.py",
        ]

        for expected_path in expected_structure:
            full_path = project_dir / expected_path
            assert full_path.exists(), f"Expected file not found: {expected_path}"

        # 6. Test configuration backup functionality
        original_description = config.project.description
        config.project.description = "Updated description"
        config.save_to_file(config_path)

        # Verify backup was created
        backup_files = list(project_dir.glob("fca-config.yaml.backup.*"))
        assert len(backup_files) >= 1

        # 7. Verify backup cleanup (should keep only recent backups)
        # Create multiple backups to test cleanup
        for i in range(10):
            config.project.description = f"Description {i}"
            config.save_to_file(config_path)

        # Check that old backups were cleaned up (should keep only 5)
        backup_files = list(project_dir.glob("fca-config.yaml.backup.*"))
        assert len(backup_files) <= 5

        print(
            f"End-to-end test completed successfully. Generated {len(generated_files)} files."
        )
