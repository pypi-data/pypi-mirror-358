# Fast Clean Architecture

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful CLI tool for scaffolding clean architecture in FastAPI projects. Generate well-structured, maintainable code following clean architecture principles with domain-driven design patterns.

## 🚀 Features

- **Clean Architecture**: Enforces separation of concerns with distinct layers
- **Domain-Driven Design**: Supports bounded contexts and domain modeling
- **Code Generation**: Automated scaffolding for entities, repositories, services, and more
- **Template System**: Customizable Jinja2 templates for code generation
- **Type Safety**: Full type hints and Pydantic validation
- **Modern Python**: Built for Python 3.9+ with async/await support
- **Analytics & Monitoring**: Built-in usage analytics, error tracking, and health monitoring
- **Security Features**: Template validation, input sanitization, and secure file operations
- **Batch Operations**: Create multiple components from YAML specifications
- **CLI Interface**: Intuitive command-line interface with rich output
- **Configuration Management**: YAML-based project configuration with versioning

## 📦 Installation

### From PyPI (Recommended)

#### Using pip
```bash
pip install fast-clean-architecture
```

#### Using Poetry
```bash
poetry add fast-clean-architecture
```

**Note**: This project uses Poetry for dependency management. The `requirements.txt` and `requirements-dev.txt` files are provided for convenience and compatibility with pip-based workflows.

## 🏗️ Architecture Overview

Fast Clean Architecture follows the clean architecture pattern with these layers:

```
📁 project_root/
├── 📁 systems/
│   └── 📁 {system_name}/
│       └── 📁 {module_name}/
│           ├── 📁 domain/           # Business logic and rules
│           │   ├── 📁 entities/     # Domain entities
│           │   ├── 📁 repositories/ # Repository interfaces
│           │   └── 📁 value_objects/# Value objects
│           ├── 📁 application/      # Use cases and services
│           │   ├── 📁 services/     # Application services
│           │   ├── 📁 commands/     # Command handlers
│           │   └── 📁 queries/      # Query handlers
│           ├── 📁 infrastructure/   # External concerns
│           │   ├── 📁 repositories/ # Repository implementations
│           │   ├── 📁 external/     # External service clients
│           │   └── 📁 models/       # Database models
│           └── 📁 presentation/     # API layer
│               ├── 📁 api/          # FastAPI routers
│               └── 📁 schemas/      # Pydantic schemas
└── 📄 fca_config.yaml             # Project configuration
```

## 📋 Prerequisites

**Important**: This tool is designed to scaffold clean architecture components for FastAPI projects. You should have:

- **Python 3.9+** installed on your system
- **Basic understanding of FastAPI** and web API development
- **Familiarity with clean architecture principles** (recommended but not required)
- **A new or existing directory** where you want to create your FastAPI project structure

**Note**: This tool generates the architectural foundation and components for your FastAPI application. You'll need to create the main FastAPI application instance (`main.py`) using the FastAPI CLI and configure dependency injection to wire everything together.

## 🔄 FastAPI Developer Workflow Integration

Fast Clean Architecture fits seamlessly into the modern FastAPI development workflow:

```mermaid
graph TD
    A[Create Default FastAPI Project in your directory of choice] --> B[Install FCA Tool]
    B --> C[Initialize FCA in Project]
    C --> D[Generate System Contexts]
    D --> E[Create Domain Modules]
    E --> F[Generate Components]
    F --> G[Wire Dependencies]
    G --> H[Implement Business Logic]
    H --> I[Add Tests]
    I --> J[Deploy Application]
```

### Workflow Steps:

1. **FastAPI Project Creation**: Create your FastAPI project instance and basic structure using either Poetry or pip
2. **FCA Installation & Setup**: Install FCA tool and initialize the clean architecture foundation
3. **Component Generation**: Generate entities, repositories, services, and API routers
4. **FastAPI Integration**: Update your `main.py` and include generated routers
5. **Dependency Injection**: Wire up services and repositories using FastAPI's DI system
6. **Business Logic**: Implement your domain-specific logic in the generated components
7. **Testing & Deployment**: Add tests and deploy your well-structured application

## 🚀 Quick Start

### 1. Create and Initialize Your FastAPI Project using Poetry

```bash
# Instantiate a new Poetry project
poetry new --flat my-fastapi-project --name custom_app_folder
cd my-fastapi-project

# Add FastAPI and Uvicorn
poetry add fastapi
poetry add uvicorn

# Create a basic main.py file
cat > main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI(
    title="My Clean Architecture API",
    description="FastAPI application with clean architecture",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
EOF

# Test your FastAPI application
uvicorn custom_app_folder.main:app
```

### 2. Install and Initialize FCA

```bash
# Install Fast Clean Architecture tool
pip install fast-clean-architecture

# Interactive initialization
fca-scaffold init

# Or with arguments
fca-scaffold init --name "my-project" --description "My FastAPI project"
```

### 3. Create a System Context

```bash
# Create a new bounded context
fca-scaffold create-system-context user-management --description "User management system"
```

### 4. Create a Module

```bash
# Create a module within a system
fca-scaffold create-module user-management users --description "User domain module"
```

### 5. Generate Components

```bash
# Generate a complete domain entity
fca-scaffold create-component user-management users entities user

# Generate repository interface
fca-scaffold create-component user-management users repositories user

# Generate application service
fca-scaffold create-component user-management users services user

# Generate API router
fca-scaffold create-component user-management users api user
```

### 6. Integrate Generated Components

**Important**: Now enhance your existing `main.py` to include the generated routers and wire everything together.

Update your `main.py` to include the generated routers:

```python
# main.py (enhanced with generated components)
from fastapi import FastAPI
from systems.user_management.users.presentation.api.user_router import router as user_router

app = FastAPI(
    title="My Clean Architecture API",
    description="FastAPI application with clean architecture",
    version="1.0.0"
)

# Include generated routers
app.include_router(user_router, prefix="/api/v1", tags=["users"])

# Add middleware, exception handlers, startup events, etc.

@app.get("/")
async def root():
    return {"message": "Clean Architecture API is running!"}
```

### 7. Run Your Application

```bash
# Install FastAPI and uvicorn if not already installed
pip install fastapi uvicorn

# Run the application
uvicorn main:app --reload

# Or run directly
python main.py
```

Your API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`.

## 📚 Detailed Usage

### Component Types

| Layer | Component | Description |
|-------|-----------|-------------|
| **Domain** | `entities` | Core business entities with domain logic |
| | `repositories` | Repository interfaces (abstract) |
| | `value_objects` | Immutable value objects |
| **Application** | `services` | Application services and use cases |
| | `commands` | Command handlers (CQRS) |
| | `queries` | Query handlers (CQRS) |
| **Infrastructure** | `repositories` | Repository implementations |
| | `external` | External service clients |
| | `models` | Database/ORM models |
| **Presentation** | `api` | FastAPI routers and endpoints |
| | `schemas` | Pydantic request/response schemas |

### CLI Commands

#### Core Commands
```bash
# Project initialization
fca-scaffold init                    # Initialize new project
fca-scaffold create-system-context   # Create system (bounded context)
fca-scaffold create-module          # Create module within system
fca-scaffold create-component       # Create individual components
```

#### Batch Operations
```bash
# Create multiple components from YAML specification
fca-scaffold batch-create components_spec.yaml
fca-scaffold batch-create my-spec.yaml --dry-run  # Preview only
```

#### Project Management
```bash
# Project status and configuration
fca-scaffold status                  # Show project overview
fca-scaffold config show            # Display configuration
fca-scaffold config validate        # Validate configuration
fca-scaffold system-status          # Show system health and analytics
```

#### Help and Information
```bash
# Get help and version info
fca-scaffold version                # Show version information
fca-scaffold --help                 # General help
```

#### Global Options
```bash
# Available for most commands
--dry-run    # Preview changes without writing files
--force      # Overwrite existing files
--verbose    # Detailed output
--config     # Specify custom config file
```

### Configuration File

The `fca_config.yaml` file tracks your project structure:

```yaml
project:
  name: my-project
  description: My FastAPI project
  version: 0.1.0
  created_at: 2024-01-15T10:30:00Z
  updated_at: 2024-01-15T10:30:00Z
  systems:
    user-management:
      description: User management system
      created_at: 2024-01-15T10:35:00Z
      updated_at: 2024-01-15T10:35:00Z
      modules:
        users:
          description: User domain module
          created_at: 2024-01-15T10:40:00Z
          updated_at: 2024-01-15T10:40:00Z
          components:
            domain:
              entities: ["user"]
              repositories: ["user"]
            application:
              services: ["user"]
            presentation:
              api: ["user"]
```

## 📊 Batch Component Creation

### YAML Specification Format

Create multiple components efficiently using YAML specifications:

```yaml
# components_spec.yaml
systems:
  - name: admin
    description: "Admin management system"
    modules:
      - name: authentication
        description: "Admin authentication module"
        components:
          domain:
            entities: [AdminUser, AdminRole]
            value_objects: [AdminEmail, AdminPassword]
            repositories: [AdminUserRepository]
          application:
            services: [AdminAuthService]
            commands: [CreateAdminUser, UpdateAdminUser]
            queries: [GetAdminUser, ListAdminUsers]
          infrastructure:
            repositories: [AdminUserRepository]
            models: [AdminUserModel]
            external: [AdminEmailService]
          presentation:
            api: [AdminAuthRouter]
            schemas: [AdminUserSchema, AdminAuthSchema]
```

### Usage

```bash
# Create all components from specification
fca-scaffold batch-create components_spec.yaml

# Preview what would be created
fca-scaffold batch-create components_spec.yaml --dry-run

# Force overwrite existing files
fca-scaffold batch-create components_spec.yaml --force
```

## 📊 System Monitoring

### Health and Analytics

Fast Clean Architecture includes built-in monitoring capabilities:

```bash
# View system health and usage analytics
fca-scaffold system-status

# Detailed system information
fca-scaffold system-status --verbose
```

**Features:**
- **Usage Analytics**: Track command usage and component creation patterns
- **Error Tracking**: Monitor and log errors with detailed context
- **Health Monitoring**: System resource usage and performance metrics
- **Security Monitoring**: Template validation and input sanitization tracking

## 🎨 Customization

### Custom Templates

You can customize the generated code by modifying templates:

1. Copy the default templates:
   ```bash
   cp -r $(python -c "import fast_clean_architecture; print(fast_clean_architecture.__path__[0])")/templates ./custom_templates
   ```

2. Modify templates in `./custom_templates/`

3. Use custom templates:
   ```bash
   fca-scaffold create-component --template-dir ./custom_templates user-management users entities user
   ```

### Template Variables

Templates have access to these variables:

```jinja2
{# System context #}
{{ system_name }}        # snake_case
{{ SystemName }}         # PascalCase
{{ system_name_camel }}  # camelCase

{# Module context #}
{{ module_name }}        # snake_case
{{ ModuleName }}         # PascalCase
{{ module_name_camel }}  # camelCase

{# Component context #}
{{ component_name }}     # snake_case
{{ ComponentName }}      # PascalCase
{{ component_name_camel }}# camelCase

{# Import paths #}
{{ entity_import }}      # Relative import path
{{ repository_import }}  # Relative import path
{{ service_import }}     # Relative import path

{# Metadata #}
{{ generated_at }}       # ISO timestamp
{{ generator_version }}  # Tool version
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fast_clean_architecture

# Run specific test file
pytest tests/test_cli.py

# Run with verbose output
pytest -v
```

## 🔧 Development

### Setup Development Environment

```bash
git clone https://github.com/alden-technologies/fast-clean-architecture.git
cd fast-clean-architecture
poetry install --with dev
```

### Code Quality

```bash
# Format code
black fast_clean_architecture tests

# Sort imports
isort fast_clean_architecture tests

# Type checking
mypy fast_clean_architecture

# Security scanning
bandit -r fast_clean_architecture

# Dependency scanning
safety check
```

### Security Updates

This project maintains up-to-date dependencies with security patches:

- **Black 24.3.0+**: Fixes CVE-2024-21503 (ReDoS vulnerability)
- **Pip 25.0+**: Fixes PVE-2025-75180 (malicious wheel execution)
- **Setuptools 78.1.1+**: Fixes CVE-2025-47273 (path traversal vulnerability)

All dependencies are pinned with SHA256 hashes for supply chain security.

### Pre-commit Hooks

```bash
poetry run pre-commit install
```

## 📖 Examples

### E-commerce System

```bash
# Initialize project
fca-scaffold init --name "ecommerce-api"

# Create systems
fca-scaffold create-system-context catalog --description "Product catalog"
fca-scaffold create-system-context orders --description "Order management"
fca-scaffold create-system-context payments --description "Payment processing"

# Create modules
fca-scaffold create-module catalog products
fca-scaffold create-module catalog categories
fca-scaffold create-module orders orders
fca-scaffold create-module orders cart
fca-scaffold create-module payments payments

# Generate components
fca-scaffold create-component catalog products entities product
fca-scaffold create-component catalog products repositories product
fca-scaffold create-component catalog products services product
fca-scaffold create-component catalog products api product
```

### Blog System

```bash
# Initialize
fca-scaffold init --name "blog-api"

# Create system
fca-scaffold create-system-context blog

# Create modules
fca-scaffold create-module blog posts
fca-scaffold create-module blog authors
fca-scaffold create-module blog comments

# Generate full stack for posts
fca-scaffold create-component blog posts entities post
fca-scaffold create-component blog posts repositories post
fca-scaffold create-component blog posts services post
fca-scaffold create-component blog posts api post
fca-scaffold create-component blog posts schemas post
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for your changes
5. Run the test suite: `pytest`
6. Run code quality checks: `black . && isort . && mypy .`
7. Commit your changes: `git commit -m 'Add amazing feature'`
8. Push to the branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Uncle Bob's Clean Architecture
- Built with [Typer](https://typer.tiangolo.com/) for the CLI
- Templates powered by [Jinja2](https://jinja.palletsprojects.com/)
- Configuration management with [Pydantic](https://pydantic-docs.helpmanual.io/)

## 📞 Support

- 📧 Email: [opensource@aldentechnologies.com](mailto:opensource@aldentechnologies.com)
- 🐛 Issues: [GitHub Issues](https://github.com/alden-technologies/fast-clean-architecture/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/alden-technologies/fast-clean-architecture/discussions)

---

**Made with ❤️ by [Adegbenga Agoro](https://www.adegbengaagoro.co), [Founder of Alden Technologies](https://www.aldentechnologies.com)**