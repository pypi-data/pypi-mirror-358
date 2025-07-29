"""Command-line interface for fast-clean-architecture."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

from .config import Config
from .generators import PackageGenerator, ComponentGenerator, ConfigUpdater
from .utils import (
    sanitize_name,
    validate_python_identifier,
)
from .exceptions import (
    FastCleanArchitectureError,
    ValidationError,
)

# Create the main Typer app
app = typer.Typer(
    name="fca-scaffold",
    help="Fast Clean Architecture scaffolding tool for FastAPI projects",
    rich_markup_mode="rich",
)

# Create console for rich output
console = Console()

# Global options
DRY_RUN_OPTION = typer.Option(
    False,
    "--dry-run",
    "-d",
    help="Show what would be created without actually creating files",
)
FORCE_OPTION = typer.Option(
    False, "--force", "-f", help="Overwrite existing files without confirmation"
)
VERBOSE_OPTION = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
CONFIG_PATH_OPTION = typer.Option(
    "fca-config.yaml", "--config", "-c", help="Path to configuration file"
)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path.cwd()


def get_config_path(config_file: str) -> Path:
    """Get the full path to the configuration file."""
    config_path = Path(config_file)
    if not config_path.is_absolute():
        config_path = get_project_root() / config_path
    return config_path


def handle_error(error: Exception, verbose: bool = False) -> None:
    """Handle and display errors consistently."""
    if isinstance(error, FastCleanArchitectureError):
        console.print(f"[red]Error:[/red] {error}")
    else:
        console.print(f"[red]Unexpected error:[/red] {error}")

    if verbose:
        console.print_exception()

    sys.exit(1)


@app.command()
def init(
    name: Optional[str] = typer.Argument(None, help="Project name"),
    description: Optional[str] = typer.Option(
        None, "--description", "--desc", help="Project description"
    ),
    version: Optional[str] = typer.Option("0.1.0", "--version", help="Project version"),
    config_file: str = CONFIG_PATH_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Initialize a new Fast Clean Architecture project."""
    try:
        project_root = get_project_root()
        config_path = get_config_path(config_file)

        # Check if config already exists
        if config_path.exists() and not force:
            if not Confirm.ask(
                f"Configuration file {config_path} already exists. Overwrite?"
            ):
                console.print("[yellow]Initialization cancelled.[/yellow]")
                return

        # Get project name if not provided
        if not name:
            name = Prompt.ask("Project name", default=project_root.name)

        # Sanitize project name
        sanitized_name = sanitize_name(name)
        if not validate_python_identifier(sanitized_name):
            raise ValidationError(f"Invalid project name: {name}")

        # Get description if not provided
        if not description:
            description = Prompt.ask("Project description", default="")

        # Create configuration
        config = Config.create_default()
        config.project.name = sanitized_name
        config.project.description = description
        config.project.version = version or "0.1.0"

        # Save configuration
        config.save_to_file(config_path)

        # Create basic project structure
        systems_dir = project_root / "systems"
        systems_dir.mkdir(exist_ok=True)

        console.print(
            Panel.fit(
                f"[green]✅ Project '{sanitized_name}' initialized successfully![/green]\n"
                f"Configuration saved to: {config_path}\n"
                f"Systems directory created: {systems_dir}",
                title="Project Initialized",
            )
        )

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def create_system_context(
    name: str = typer.Argument(..., help="System context name"),
    description: Optional[str] = typer.Option(
        None, "--description", "--desc", help="System description"
    ),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create a new system context."""
    try:
        project_root = get_project_root()
        config_path = get_config_path(config_file)

        # Sanitize system name
        sanitized_name = sanitize_name(name)
        if not validate_python_identifier(sanitized_name):
            raise ValidationError(f"Invalid system name: {name}")

        # Initialize generators
        config_updater = ConfigUpdater(config_path, console)
        package_generator = PackageGenerator(console)

        # Create system structure
        package_generator.create_system_structure(
            base_path=project_root,
            system_name=sanitized_name,
            dry_run=dry_run,
        )

        if not dry_run:
            # Update configuration
            config_updater.add_system(sanitized_name, description)

        console.print(
            f"[green]✅ System context '{sanitized_name}' created successfully![/green]"
        )

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def create_module(
    system_name: str = typer.Argument(..., help="System context name"),
    module_name: str = typer.Argument(..., help="Module name"),
    description: Optional[str] = typer.Option(
        None, "--description", "--desc", help="Module description"
    ),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create a new module within a system context."""
    try:
        project_root = get_project_root()
        config_path = get_config_path(config_file)

        # Sanitize names
        sanitized_system = sanitize_name(system_name)
        sanitized_module = sanitize_name(module_name)

        if not validate_python_identifier(sanitized_system):
            raise ValidationError(f"Invalid system name: {system_name}")
        if not validate_python_identifier(sanitized_module):
            raise ValidationError(f"Invalid module name: {module_name}")

        # Initialize generators
        config_updater = ConfigUpdater(config_path, console)
        package_generator = PackageGenerator(console)

        # Create module structure
        package_generator.create_module_structure(
            base_path=project_root,
            system_name=sanitized_system,
            module_name=sanitized_module,
            dry_run=dry_run,
        )

        if not dry_run:
            # Update configuration
            config_updater.add_module(sanitized_system, sanitized_module, description)

        console.print(
            f"[green]✅ Module '{sanitized_module}' created in system '{sanitized_system}'![/green]"
        )

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def create_component(
    location: str = typer.Argument(
        ..., help="Component location (system/module/layer/type)"
    ),
    name: str = typer.Argument(..., help="Component name"),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create a new component.

    Location format: system_name/module_name/layer/component_type
    Example: user_management/authentication/domain/entities
    """
    try:
        project_root = get_project_root()
        config_path = get_config_path(config_file)

        # Parse location
        location_parts = location.split("/")
        if len(location_parts) != 4:
            raise ValidationError(
                "Location must be in format: system_name/module_name/layer/component_type"
            )

        system_name, module_name, layer, component_type = location_parts

        # Sanitize names
        sanitized_system = sanitize_name(system_name)
        sanitized_module = sanitize_name(module_name)
        sanitized_name = sanitize_name(name)

        if not all(
            [
                validate_python_identifier(sanitized_system),
                validate_python_identifier(sanitized_module),
                validate_python_identifier(sanitized_name),
            ]
        ):
            raise ValidationError("Invalid names provided")

        # Initialize generators
        config_updater = ConfigUpdater(config_path, console)
        component_generator = ComponentGenerator(config_updater.config, console)

        # Create component
        file_path = component_generator.create_component(
            base_path=project_root,
            system_name=sanitized_system,
            module_name=sanitized_module,
            layer=layer,
            component_type=component_type,
            component_name=sanitized_name,
            dry_run=dry_run,
            force=force,
        )

        if not dry_run:
            # Update configuration
            config_updater.add_component(
                system_name=sanitized_system,
                module_name=sanitized_module,
                layer=layer,
                component_type=component_type,
                component_name=sanitized_name,
                file_path=file_path,
            )

        console.print(
            f"[green]✅ Component '{sanitized_name}' created at {location}![/green]"
        )

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def batch_create(
    spec_file: str = typer.Argument(..., help="YAML specification file"),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create multiple components from a YAML specification file."""
    try:
        import yaml

        project_root = get_project_root()
        config_path = get_config_path(config_file)
        spec_path = Path(spec_file)

        if not spec_path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_file}")

        # Load specification
        with open(spec_path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)

        # Initialize generators
        config_updater = ConfigUpdater(config_path, console)
        component_generator = ComponentGenerator(config_updater.config, console)

        # Process specification
        for system_spec in spec.get("systems", []):
            system_name = system_spec["name"]

            for module_spec in system_spec.get("modules", []):
                module_name = module_spec["name"]
                components_spec = module_spec.get("components", {})

                # Create components
                component_generator.create_multiple_components(
                    base_path=project_root,
                    system_name=system_name,
                    module_name=module_name,
                    components_spec=components_spec,
                    dry_run=dry_run,
                    force=force,
                )

        console.print("[green]✅ Batch creation completed![/green]")

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def status(
    config_file: str = CONFIG_PATH_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Show project status and configuration summary."""
    try:
        config_path = get_config_path(config_file)

        if not config_path.exists():
            console.print(
                "[yellow]No configuration file found. Run 'fca-scaffold init' first.[/yellow]"
            )
            return

        # Load configuration
        config_updater = ConfigUpdater(config_path, console)
        summary = config_updater.get_config_summary()

        # Display project info
        project_info = summary["project"]
        console.print(
            Panel.fit(
                f"[bold]Name:[/bold] {project_info['name']}\n"
                f"[bold]Version:[/bold] {project_info['version']}\n"
                f"[bold]Created:[/bold] {project_info['created_at']}\n"
                f"[bold]Updated:[/bold] {project_info['updated_at']}",
                title="Project Information",
            )
        )

        # Display systems table
        if summary["systems"]:
            table = Table(title="Systems Overview")
            table.add_column("System", style="cyan")
            table.add_column("Modules", style="green")
            table.add_column("Created", style="yellow")
            table.add_column("Updated", style="magenta")

            for system_name, system_info in summary["systems"].items():
                table.add_row(
                    system_name,
                    str(len(system_info["modules"])),
                    system_info["created_at"][:10],  # Show date only
                    system_info["updated_at"][:10],
                )

            console.print(table)
        else:
            console.print("[yellow]No systems found.[/yellow]")

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def config(
    action: str = typer.Argument(..., help="Action: show, edit, validate"),
    config_file: str = CONFIG_PATH_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Manage project configuration."""
    try:
        config_path = get_config_path(config_file)

        if action == "show":
            if not config_path.exists():
                console.print("[yellow]No configuration file found.[/yellow]")
                return

            # Display configuration content
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()

            syntax = Syntax(content, "yaml", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Configuration: {config_path}"))

        elif action == "validate":
            if not config_path.exists():
                console.print("[red]Configuration file not found.[/red]")
                return

            try:
                Config.load_from_file(config_path)
                console.print("[green]✅ Configuration is valid![/green]")
            except Exception as e:
                console.print(f"[red]❌ Configuration is invalid: {e}[/red]")

        elif action == "edit":
            console.print(
                f"[yellow]Please edit the configuration file manually: {config_path}[/yellow]"
            )

        else:
            console.print(f"[red]Unknown action: {action}[/red]")
            console.print("Available actions: show, edit, validate")

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__, __author__

    console.print(
        Panel.fit(
            f"[bold]Fast Clean Architecture[/bold]\n"
            f"Version: {__version__}\n"
            f"Author: {__author__}",
            title="Version Information",
        )
    )


if __name__ == "__main__":
    app()
