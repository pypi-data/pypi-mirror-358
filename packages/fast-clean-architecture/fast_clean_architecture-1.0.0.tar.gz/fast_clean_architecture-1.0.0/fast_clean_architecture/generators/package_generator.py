"""Package generator for creating directory structures and __init__.py files."""

from pathlib import Path
from typing import List, Dict, Optional

import jinja2
from rich.console import Console

from ..templates import TEMPLATES_DIR
from ..utils import ensure_directory
from ..exceptions import TemplateError


class PackageGenerator:
    """Generator for creating Python packages with proper __init__.py files."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def create_system_structure(
        self, base_path: Path, system_name: str, dry_run: bool = False
    ) -> None:
        """Create the complete system directory structure."""
        system_path = base_path / "systems" / system_name

        if dry_run:
            self.console.print(
                f"[yellow]DRY RUN:[/yellow] Would create system structure: {system_path}"
            )
            return

        # Create systems root if it doesn't exist
        systems_root = base_path / "systems"
        if not systems_root.exists():
            ensure_directory(systems_root)
            self._create_init_file(
                systems_root / "__init__.py",
                package_type="empty",
                package_description="Systems",
                context="fast-clean-architecture",
            )

        # Create system directory
        ensure_directory(system_path)

        # Create system __init__.py
        self._create_init_file(
            system_path / "__init__.py",
            package_type="system",
            system_name=system_name,
        )

        # Create main.py for system entry point
        main_content = f'"""\nMain entry point for {system_name} system.\n"""\n\n# System initialization and configuration\n'
        (system_path / "main.py").write_text(main_content, encoding="utf-8")

        self.console.print(f"✅ Created system structure: {system_path}")

    def create_module_structure(
        self, base_path: Path, system_name: str, module_name: str, dry_run: bool = False
    ) -> None:
        """Create the complete module directory structure."""
        module_path = base_path / "systems" / system_name / module_name

        if dry_run:
            self.console.print(
                f"[yellow]DRY RUN:[/yellow] Would create module structure: {module_path}"
            )
            return

        # Create module directory
        ensure_directory(module_path)

        # Create module __init__.py
        self._create_init_file(
            module_path / "__init__.py",
            package_type="module",
            module_name=module_name,
            system_name=system_name,
        )

        # Create layer directories
        layers = {
            "domain": {
                "entities": [],
                "repositories": [],
                "value_objects": [],
            },
            "application": {
                "services": [],
                "commands": [],
                "queries": [],
            },
            "infrastructure": {
                "models": [],
                "repositories": [],
                "external": [],
                "internal": [],
            },
            "presentation": {
                "api": [],
                "schemas": [],
            },
        }

        for layer_name, components in layers.items():
            layer_path = module_path / layer_name
            ensure_directory(layer_path)

            # Create layer __init__.py
            self._create_init_file(
                layer_path / "__init__.py",
                package_type="empty",
                package_description=layer_name.title(),
                context=f"{module_name} module",
            )

            # Create component directories
            for component_type in components:
                component_path = layer_path / component_type
                ensure_directory(component_path)

                # Create component __init__.py
                self._create_init_file(
                    component_path / "__init__.py",
                    package_type="component",
                    component_type=component_type,
                    module_name=module_name,
                    components=[],
                )

        # Create module.py file
        module_content = f'"""\nModule registration for {module_name}.\n"""\n\n# Module configuration and dependencies\n'
        (module_path / "module.py").write_text(module_content, encoding="utf-8")

        self.console.print(f"✅ Created module structure: {module_path}")

    def update_component_init(
        self,
        component_path: Path,
        component_type: str,
        module_name: str,
        components: List[Dict[str, str]],
    ) -> None:
        """Update component __init__.py with new imports."""
        init_path = component_path / "__init__.py"

        self._create_init_file(
            init_path,
            package_type="component",
            component_type=component_type,
            module_name=module_name,
            components=components,
        )

        self.console.print(f"📝 Updated {init_path}")

    def _create_init_file(self, file_path: Path, **template_vars) -> None:
        """Create __init__.py file from template."""
        try:
            template = self.template_env.get_template("__init__.py.j2")
            content = template.render(**template_vars)

            file_path.write_text(content, encoding="utf-8")

        except jinja2.TemplateError as e:
            raise TemplateError(f"Error rendering __init__.py template: {e}")
        except Exception as e:
            raise TemplateError(f"Error creating __init__.py file: {e}")
