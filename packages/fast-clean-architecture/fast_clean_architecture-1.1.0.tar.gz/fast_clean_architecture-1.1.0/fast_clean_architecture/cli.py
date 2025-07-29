"""Command-line interface for fast-clean-architecture."""

import os
import sys
from pathlib import Path
from typing import List, NoReturn, Optional, Union, cast

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from .analytics import log_usage_summary, track_command_usage, track_component_creation
from .config import Config
from .error_tracking import log_error_summary, track_error
from .exceptions import FastCleanArchitectureError, ValidationError
from .generators import ConfigUpdater, PackageGenerator
from .generators.generator_factory import create_generator_factory
from .health import log_startup_health
from .logging_config import configure_logging, get_logger
from .utils import sanitize_name, validate_name, validate_python_identifier

# Configure structured logging
configure_logging()
logger = get_logger(__name__)

# Log startup health
log_startup_health()

# Create the main Typer app
app = typer.Typer(
    name="fca-scaffold",
    help="""[bold blue]Fast Clean Architecture[/bold blue] is a scaffolding tool for FastAPI projects.

[bold]Quick Start:[/bold]
  1. Initialize a new project
     [cyan]fca-scaffold init[/cyan]

  2. Create a system context
     [cyan]fca-scaffold create-system-context admin[/cyan]

  3. Create a module in the admin system
     [cyan]fca-scaffold create-module admin auth[/cyan]

  4. Create a component (e.g., entities, services, repositories)
     [cyan]fca-scaffold create-component admin/auth/domain/entities Admin[/cyan]

[bold]Definitions:[/bold]
  [yellow]System:[/yellow]
    A bounded context representing a major business domain.
    Examples: user_management, payment_processing

  [yellow]Module:[/yellow]
    A functional area within a system that groups related components.
    Examples: auth, billing, notifications

  [yellow]Component:[/yellow]
    Individual code artifacts within Clean Architecture layers:

      [dim]Domain:[/dim]
        - entities
        - repositories
        - value_objects

      [dim]Application:[/dim]
        - services
        - commands
        - queries

      [dim]Infrastructure:[/dim]
        - models
        - repositories
        - external

      [dim]Presentation:[/dim]
        - api
        - schemas

[bold]Get help for any command:[/bold]
  [cyan]fca-scaffold [COMMAND] --help[/cyan]

[bold]Examples:[/bold]
  Initialize a project with a description:
    [dim]fca-scaffold init my-project --description "My FastAPI project"[/dim]

  Check scaffold status:
    [dim]fca-scaffold status[/dim]

  Show current config:
    [dim]fca-scaffold config show[/dim]
    """,
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
    "fca_config.yaml", "--config", "-c", help="Path to configuration file"
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


def handle_error(error: Exception, verbose: bool = False) -> NoReturn:
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
    name: Optional[str] = typer.Argument(
        None, help="Project name (will be sanitized for Python compatibility)"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "--desc", help="Project description for documentation"
    ),
    version: Optional[str] = typer.Option(
        "0.1.0", "--version", help="Initial project version (semantic versioning)"
    ),
    config_file: str = CONFIG_PATH_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Initialize a new Fast Clean Architecture project.

    Creates a new FCA project with configuration file and basic directory structure.
    If no name is provided, you'll be prompted to enter one.

    [bold]Examples:[/bold]
      [cyan]fca-scaffold init[/cyan]                                    # Interactive mode
      [cyan]fca-scaffold init my-api[/cyan]                            # With project name
      [cyan]fca-scaffold init my-api --desc "User management API"[/cyan]  # With description
      [cyan]fca-scaffold init my-api --version 1.0.0 --force[/cyan]       # Overwrite existing

    [bold]What it creates:[/bold]
      • [dim]fca_config.yaml[/dim] - Project configuration file
      • [dim]systems/[/dim] - Directory for system contexts
    """
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
    name: str = typer.Argument(
        ..., help="System context name (e.g., admin, customer, settings)"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "--desc", help="Description of what this system handles"
    ),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create a new system context.

    A system context represents a bounded context in your domain, containing related
    business functionality or aimed at different operational context such as admin, customer, settings. Each system can contain multiple modules.

    [bold]Examples:[/bold]
      [cyan]fca-scaffold create-system-context admin[/cyan]
      [cyan]fca-scaffold create-system-context customer --desc "Customer System"[/cyan]
      [cyan]fca-scaffold create-system-context settings --dry-run[/cyan]  # Preview only

    [bold]What it creates:[/bold]
      • [dim]systems/[SYSTEM_NAME]/[/dim] - System directory
      • [dim]systems/[SYSTEM_NAME]/__init__.py[/dim] - Python package file
      • Updates [dim]fca_config.yaml[/dim] with system information

    [bold]Next steps:[/bold]
      Create modules with: [cyan]fca-scaffold create-module [SYSTEM_NAME] [MODULE_NAME][/cyan]
    """
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
    system_name: str = typer.Argument(..., help="Existing system context name"),
    module_name: str = typer.Argument(
        ..., help="Module name (e.g., authentication, user_profile)"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "--desc", help="Description of module functionality"
    ),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create a new module within a system context.

    Modules organize related functionality within a system context, following
    Clean Architecture layers (domain, application, infrastructure, presentation).

    [bold]Examples:[/bold]
      [cyan]fca-scaffold create-module admin authentication[/cyan]
      [cyan]fca-scaffold create-module customer payment_processing --desc "Payment processing logic"[/cyan]
      [cyan]fca-scaffold create-module settings notification_settings --dry-run[/cyan]  # Preview only

    [bold]What it creates:[/bold]
      • [dim]systems/[SYSTEM_NAME]/modules/[MODULE_NAME]/[/dim] - Module directory
      • [dim]systems/[SYSTEM_NAME]/modules/[MODULE_NAME]/__init__.py[/dim] - Package file
      • [dim]systems/[SYSTEM_NAME]/modules/[MODULE_NAME]/[MODULE_NAME]_module_api.py[/dim] - Module API file
      • [dim]systems/[SYSTEM_NAME]/modules/[MODULE_NAME]/domain/[/dim] - Domain layer
      • [dim]systems/[SYSTEM_NAME]/modules/[MODULE_NAME]/application/[/dim] - Application layer
      • [dim]systems/[SYSTEM_NAME]/modules/[MODULE_NAME]/infrastructure/[/dim] - Infrastructure layer
      • [dim]systems/[SYSTEM_NAME]/modules/[MODULE_NAME]/presentation/[/dim] - Presentation layer
      • Updates [dim]fca_config.yaml[/dim] with module information

    [bold]Next steps:[/bold]
      Create components with: [cyan]fca-scaffold create-component [SYSTEM_NAME]/[MODULE_NAME]/[LAYER]/[TYPE] [COMPONENT_NAME][/cyan]
    """
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
        ...,
        help="Component location: system/module/layer/type (e.g., user_management/auth/domain/entities)",
    ),
    name: str = typer.Argument(
        ..., help="Component name (e.g., User, AuthService, UserRepository)"
    ),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create a new component.

    Creates components following Clean Architecture patterns. Components are generated
    from templates and placed in the appropriate layer directory.

    [bold]Location format:[/bold] [cyan]system_name/module_name/layer/component_type[/cyan]

    [bold]Available layers and component types:[/bold]
      [yellow]domain/[/yellow]
        • [cyan]entities[/cyan] - Domain entities (business objects)
        • [cyan]value_objects[/cyan] - Value objects (immutable data)
        • [cyan]repositories[/cyan] - Repository interfaces
        • [cyan]services[/cyan] - Domain services

      [yellow]application/[/yellow]
        • [cyan]commands[/cyan] - Command handlers (CQRS)
        • [cyan]queries[/cyan] - Query handlers (CQRS)
        • [cyan]services[/cyan] - Application services

      [yellow]infrastructure/[/yellow]
        • [cyan]models[/cyan] - Database models and schemas
        • [cyan]repositories[/cyan] - Repository implementations
        • [cyan]external[/cyan] - External service adapters

      [yellow]presentation/[/yellow]
        • [cyan]api[/cyan] - API endpoints/controllers
        • [cyan]schemas[/cyan] - Request/response schemas

    [bold]Examples:[/bold]
      [cyan]fca-scaffold create-component admin/auth/domain/entities User[/cyan]
      [cyan]fca-scaffold create-component admin/auth/application/commands CreateUser[/cyan]
      [cyan]fca-scaffold create-component customer/payment_processing/infrastructure/repositories PaymentProcessingRepository[/cyan]
      [cyan]fca-scaffold create-component settings/notification_settings/presentation/api NotificationSettingsAPI[/cyan]

    [bold]What it creates:[/bold]
      • Python file with component implementation
      • Imports and dependencies based on component type
      • Updates [dim]fca_config.yaml[/dim] with component information
    """
    try:
        # Log CLI command start
        logger.info(
            "CLI create_component command started",
            operation="cli_create_component",
            location=location,
            name=name,
            dry_run=dry_run,
            force=force,
        )

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

        # Initialize generators using factory pattern
        config_updater = ConfigUpdater(config_path, console)
        generator_factory = create_generator_factory(config_updater.config, console)
        component_generator = generator_factory.create_generator("component")

        # Cast to ComponentGeneratorProtocol for type safety
        from .generators import ComponentGeneratorProtocol

        component_gen = cast(ComponentGeneratorProtocol, component_generator)

        # Create component
        file_path = component_gen.create_component(
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

        # Log successful completion
        logger.info(
            "CLI create_component command completed successfully",
            operation="cli_create_component",
            component_name=sanitized_name,
            location=location,
            file_path=str(file_path) if not dry_run else None,
        )

        # Track component creation for analytics
        if not dry_run:
            track_component_creation(
                system_name=sanitized_system,
                module_name=sanitized_module,
                layer=layer,
                component_type=component_type,
                component_name=sanitized_name,
            )

    except Exception as e:
        # Log CLI error and track it
        logger.error(
            "CLI create_component command failed",
            operation="cli_create_component",
            error=str(e),
            error_type=type(e).__name__,
            location=location,
            name=name,
        )

        # Track the error for analytics
        track_error(
            error=e,
            context={
                "command": "create_component",
                "location": location,
                "name": name,
                "dry_run": dry_run,
                "force": force,
            },
            operation="cli_create_component",
        )

        handle_error(e, verbose)


@app.command()
def batch_create(
    spec_file: str = typer.Argument(
        ..., help="Path to YAML specification file (see examples/components_spec.yaml)"
    ),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create multiple components from a YAML specification file.

    Batch creation allows you to define multiple systems, modules, and components
    in a single YAML file and create them all at once.

    [bold]Examples:[/bold]
      [cyan]fca-scaffold batch-create components_spec.yaml[/cyan]
      [cyan]fca-scaffold batch-create my-spec.yaml --dry-run[/cyan]  # Preview only

    [bold]Specification file format:[/bold]
      [dim]systems:[/dim]
      [dim]  - name: admin[/dim]
      [dim]    modules:[/dim]
      [dim]      - name: authentication[/dim]
      [dim]        components:[/dim]
      [dim]          domain:[/dim]
      [dim]            entities: [AdminUser, AdminRole][/dim]
      [dim]            value_objects: [AdminEmail, AdminPassword][/dim]
      [dim]            repositories: [AdminUserRepository][/dim]
      [dim]          application:[/dim]
      [dim]            commands: [CreateAdminUser, UpdateAdminUser][/dim]

    [bold]See also:[/bold]
      Check [cyan]examples/components_spec.yaml[/cyan] for a complete example
    """
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

        # Initialize generators using factory pattern
        config_updater = ConfigUpdater(config_path, console)
        generator_factory = create_generator_factory(config_updater.config, console)
        component_generator = generator_factory.create_generator("component")

        # Process specification
        for system_spec in spec.get("systems", []):
            system_name = system_spec["name"]

            for module_spec in system_spec.get("modules", []):
                module_name = module_spec["name"]
                components_spec = module_spec.get("components", {})

                # Cast to ComponentGeneratorProtocol for type safety
                from .protocols import ComponentGeneratorProtocol

                component_gen = cast(ComponentGeneratorProtocol, component_generator)

                # Create components
                component_gen.create_multiple_components(
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
    """Show project status and configuration summary.

    Displays an overview of your FCA project including systems, modules,
    and recent activity. Useful for understanding project structure.

    [bold]Examples:[/bold]
      [cyan]fca-scaffold status[/cyan]                    # Show project overview
      [cyan]fca-scaffold status --verbose[/cyan]         # Detailed information
      [cyan]fca-scaffold status -c my-config.yaml[/cyan] # Custom config file

    [bold]Information shown:[/bold]
      • Project name, version, and timestamps
      • Systems and module counts
      • Recent creation/update dates
      • Configuration file location
    """
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
    action: str = typer.Argument(..., help="Action to perform: show, edit, validate"),
    config_file: str = CONFIG_PATH_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Manage project configuration.

    Provides tools to view, edit, and validate your FCA project configuration.
    The configuration file tracks all systems, modules, and components.

    [bold]Available actions:[/bold]
      [cyan]show[/cyan]     - Display configuration file contents with syntax highlighting
      [cyan]edit[/cyan]     - Get instructions for editing the configuration
      [cyan]validate[/cyan] - Check if configuration file is valid YAML and structure

    [bold]Examples:[/bold]
      [cyan]fca-scaffold config show[/cyan]                    # View current config
      [cyan]fca-scaffold config validate[/cyan]               # Check config validity
      [cyan]fca-scaffold config show -c my-config.yaml[/cyan] # Custom config file

    [bold]Configuration structure:[/bold]
      • [dim]project[/dim] - Project metadata (name, version, description)
      • [dim]systems[/dim] - System contexts and their modules
      • [dim]components[/dim] - Generated components and their locations
      • [dim]timestamps[/dim] - Creation and modification dates
    """
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
def help_guide() -> None:
    """Show comprehensive help and quick reference guide.

    Displays a detailed guide covering all commands, common workflows,
    and best practices for using Fast Clean Architecture.

    [bold]Example:[/bold]
      [cyan]fca-scaffold help-guide[/cyan]

    [bold]Covers:[/bold]
      • Complete workflow from project init to component creation
      • Command reference with examples
      • Clean Architecture layer explanations
      • Best practices and tips
    """
    console.print(
        Panel.fit(
            "[bold blue]Fast Clean Architecture - Complete Guide[/bold blue]\n\n"
            "[bold yellow]📖 Key Definitions:[/bold yellow]\n\n"
            "[yellow]System:[/yellow]\n"
            "  A bounded context representing a major business domain.\n"
            "  Examples: admin, customer, settings\n\n"
            "[yellow]Module:[/yellow]\n"
            "  A functional area within a system that groups related components.\n"
            "  Examples: auth, billing, notifications, reporting\n\n"
            "[yellow]Component:[/yellow]\n"
            "  Individual code artifacts within Clean Architecture layers:\n\n"
            "    [dim]Domain:[/dim]\n"
            "      - entities\n"
            "      - repositories\n"
            "      - value_objects\n\n"
            "    [dim]Application:[/dim]\n"
            "      - services\n"
            "      - commands\n"
            "      - queries\n\n"
            "    [dim]Infrastructure:[/dim]\n"
            "      - models\n"
            "      - repositories\n"
            "      - external\n\n"
            "    [dim]Presentation:[/dim]\n"
            "      - api\n"
            "      - schemas\n\n"
            "[bold yellow]🚀 Quick Start Workflow:[/bold yellow]\n"
            "1. [cyan]fca-scaffold init my-project[/cyan] - Initialize project\n"
            "2. [cyan]fca-scaffold create-system-context admin[/cyan] - Create system\n"
            "3. [cyan]fca-scaffold create-module admin auth[/cyan] - Create module\n"
            "4. [cyan]fca-scaffold create-component admin/auth/domain/entities AdminUser[/cyan] - Create any component type\n\n"
            "[bold yellow]📋 Available Commands:[/bold yellow]\n"
            "• [cyan]init[/cyan] - Initialize new project\n"
            "• [cyan]create-system-context[/cyan] - Create system (bounded context)\n"
            "• [cyan]create-module[/cyan] - Create module within system\n"
            "• [cyan]create-component[/cyan] - Create individual components (entities, services, repositories, etc.)\n"
            "• [cyan]batch-create[/cyan] - Create multiple components from YAML\n"
            "• [cyan]status[/cyan] - Show project overview\n"
            "• [cyan]config[/cyan] - Manage configuration\n"
            "• [cyan]version[/cyan] - Show version info\n\n"
            "[bold yellow]🏗️ Clean Architecture Layers & Components:[/bold yellow]\n"
            "• [yellow]domain/[/yellow] - Business logic\n"
            "  ◦ entities, repositories, value_objects\n"
            "• [yellow]application/[/yellow] - Use cases\n"
            "  ◦ services, commands, queries\n"
            "• [yellow]infrastructure/[/yellow] - External concerns\n"
            "  ◦ models, repositories, external\n"
            "• [yellow]presentation/[/yellow] - User interface\n"
            "  ◦ api, schemas\n\n"
            "[bold yellow]💡 Pro Tips:[/bold yellow]\n"
            "• Use [cyan]--dry-run[/cyan] to preview changes\n"
            "• Use [cyan]--help[/cyan] with any command for detailed info\n"
            "• Check [cyan]fca-scaffold status[/cyan] to see project structure\n"
            "• Validate config with [cyan]fca-scaffold config validate[/cyan]\n\n"
            "[bold yellow]📖 For detailed help on any command:[/bold yellow]\n"
            "[cyan]fca-scaffold [COMMAND] --help[/cyan]",
            title="📚 Fast Clean Architecture - Help Guide",
        )
    )


@app.command()
def version() -> None:
    """Show version information.

    Displays the current version of Fast Clean Architecture scaffolding tool
    along with author information.

    [bold]Example:[/bold]
      [cyan]fca-scaffold version[/cyan]

    [bold]Useful for:[/bold]
      • Checking which version you're running
      • Bug reports and support requests
      • Ensuring compatibility with documentation
    """
    from . import __author__, __version__

    console.print(
        Panel.fit(
            f"[bold]Fast Clean Architecture[/bold]\n"
            f"Version: {__version__}\n"
            f"Author: {__author__}",
            title="Version Information",
        )
    )


@app.command()
def system_status(
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Show system status, health, and usage analytics.

    Displays comprehensive information about:
    - System health and resource usage
    - Error tracking summary
    - Usage analytics and productivity metrics

    [bold]Examples:[/bold]
      [cyan]fca-scaffold system-status[/cyan]
      [cyan]fca-scaffold system-status --verbose[/cyan]
    """
    try:
        from .analytics import get_analytics
        from .error_tracking import get_error_tracker
        from .health import get_health_monitor

        console.print("\n[bold blue]📊 Fast Clean Architecture Status[/bold blue]\n")

        # Health Status
        console.print("[bold yellow]🏥 System Health[/bold yellow]")
        health_monitor = get_health_monitor()
        health_data = health_monitor.get_system_health()

        if "error" in health_data:
            console.print(f"[red]❌ Health check failed: {health_data['error']}[/red]")
        else:
            process_data = health_data.get("process", {})
            system_data = health_data.get("system", {})

            console.print(
                f"  • Memory Usage: {process_data.get('memory_rss_mb', 0):.1f} MB ({process_data.get('memory_percent', 0):.1f}%)"
            )
            console.print(f"  • CPU Usage: {process_data.get('cpu_percent', 0):.1f}%")
            console.print(
                f"  • System Memory: {system_data.get('memory_used_percent', 0):.1f}% used"
            )
            console.print(
                f"  • Disk Space: {system_data.get('disk_used_percent', 0):.1f}% used"
            )
            console.print(
                f"  • Uptime: {health_data.get('uptime_seconds', 0):.1f} seconds"
            )

        # Error Tracking
        console.print("\n[bold yellow]🐛 Error Tracking[/bold yellow]")
        error_tracker = get_error_tracker()
        error_summary = error_tracker.get_error_summary()

        console.print(f"  • Total Errors: {error_summary.get('total_errors', 0)}")
        console.print(f"  • Unique Errors: {error_summary.get('unique_errors', 0)}")

        if error_summary.get("most_common_errors"):
            console.print("  • Most Common Errors:")
            for error_info in error_summary["most_common_errors"][:3]:
                console.print(
                    f"    - {error_info['signature']}: {error_info['count']} times"
                )

        # Usage Analytics
        console.print("\n[bold yellow]📈 Usage Analytics[/bold yellow]")
        analytics = get_analytics()
        usage_summary = analytics.get_usage_summary()
        productivity = analytics.get_productivity_metrics()

        session_data = usage_summary.get("session", {})
        console.print(
            f"  • Session Duration: {session_data.get('duration_seconds', 0):.1f} seconds"
        )
        console.print(f"  • Total Commands: {session_data.get('total_commands', 0)}")
        console.print(
            f"  • Components Created: {productivity.get('components_created', 0)}"
        )
        console.print(
            f"  • Components/Hour: {productivity.get('components_per_hour', 0):.1f}"
        )

        if usage_summary.get("commands"):
            console.print("  • Command Usage:")
            for command, count in list(usage_summary["commands"].items())[:3]:
                console.print(f"    - {command}: {count} times")

        if usage_summary.get("component_types"):
            console.print("  • Popular Component Types:")
            for comp_type, count in list(usage_summary["component_types"].items())[:3]:
                console.print(f"    - {comp_type}: {count} times")

        if verbose:
            # Show detailed information
            console.print("\n[bold yellow]🔍 Detailed Information[/bold yellow]")

            if usage_summary.get("layers"):
                console.print("  • Layer Usage:")
                for layer, count in usage_summary["layers"].items():
                    console.print(f"    - {layer}: {count} times")

            if usage_summary.get("systems"):
                console.print("  • System Usage:")
                for system, count in usage_summary["systems"].items():
                    console.print(f"    - {system}: {count} times")

            if usage_summary.get("performance"):
                console.print("  • Performance Metrics:")
                for command, perf in usage_summary["performance"].items():
                    console.print(
                        f"    - {command}: avg {perf['average_ms']}ms (min: {perf['min_ms']}ms, max: {perf['max_ms']}ms)"
                    )

        console.print("\n[green]✅ Status check completed[/green]")

        # Log the status check
        logger.info(
            "System status command executed",
            operation="cli_system_status",
            verbose=verbose,
        )

    except Exception as e:
        logger.error(
            "System status command failed",
            operation="cli_system_status",
            error=str(e),
            error_type=type(e).__name__,
        )
        handle_error(e, verbose)


if __name__ == "__main__":
    # Ensure logging is configured
    configure_logging()
    app()
