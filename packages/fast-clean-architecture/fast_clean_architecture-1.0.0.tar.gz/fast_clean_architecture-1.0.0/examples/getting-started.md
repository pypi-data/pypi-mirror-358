# Getting Started with Fast Clean Architecture

This guide will walk you through creating a complete FastAPI application using the Fast Clean Architecture (FCA) scaffolding tool.

## How This Tool Fits Into Your FastAPI Workflow

Fast Clean Architecture is a **scaffolding and code generation tool** that creates the architectural foundation for your FastAPI projects. Here's how it integrates into your development workflow:

### Traditional FastAPI Development:
```
Create FastAPI app → Write endpoints → Add business logic → Organize code
```

### With Fast Clean Architecture:
```
Create FastAPI app → Scaffold architecture → Generate components → Wire dependencies → Implement business logic
```

### What This Tool Provides:
- ✅ **Clean architecture structure** with proper layer separation
- ✅ **Code templates** for entities, repositories, services, and API routers
- ✅ **Consistent project organization** following DDD principles
- ✅ **Type-safe boilerplate** with Pydantic models and type hints

### What You Still Need To Do:
- 🔧 **Create the main FastAPI application** (`main.py`)
- 🔧 **Configure dependency injection** to wire components together
- 🔧 **Implement business logic** in the generated templates
- 🔧 **Set up database connections** and other infrastructure
- 🔧 **Add authentication, middleware, and error handling**

This tool accelerates the initial setup and ensures your project follows clean architecture principles from day one.

## Prerequisites

- Python 3.8 or higher
- pip package manager or Poetry
- Basic understanding of FastAPI and web API development
- Familiarity with clean architecture principles (recommended)

**Important Note**: This tool does not create a complete, runnable FastAPI application on its own. It generates the architectural components and structure for your FastAPI project. You will need to:

1. Create the main FastAPI application instance (`main.py`)
2. Configure dependency injection to wire components together
3. Add database connections and other infrastructure requirements
4. Implement your specific business logic

This guide will walk you through all these steps.

## Installation

### Using pip

```bash
pip install fast-clean-architecture
```

### Using Poetry

```bash
poetry add fast-clean-architecture
```

Or if you're starting a new project with Poetry:

```bash
# Initialize a new Poetry project
poetry init

# Add fast-clean-architecture as a dependency
poetry add fast-clean-architecture

# Activate the virtual environment
poetry shell
```

## Step 1: Initialize Your Project

First, create a new directory for your project and initialize it:

```bash
mkdir my-fastapi-app
cd my-fastapi-app

# Initialize the project
fca-scaffold init my_fastapi_app --description "My awesome FastAPI application" --version "1.0.0"
```

This creates:
- `fca-config.yaml` - Project configuration file
- `systems/` - Directory for system contexts

## Step 2: Create System Contexts

System contexts represent major functional areas of your application. Let's create a user management system:

```bash
fca-scaffold create-system-context user_management --description "User management and authentication system"
```

This creates:
```
systems/
└── user_management/
    ├── __init__.py
    └── main.py
```

## Step 3: Create Modules

Modules are logical groupings within a system context. Let's create an authentication module:

```bash
fca-scaffold create-module user_management authentication --description "User authentication and authorization"
```

This creates the complete clean architecture structure:
```
systems/
└── user_management/
    ├── __init__.py
    ├── main.py
    └── authentication/
        ├── __init__.py
        ├── domain/
        │   ├── __init__.py
        │   ├── entities/
        │   │   └── __init__.py
        │   ├── repositories/
        │   │   └── __init__.py
        │   └── value_objects/
        │       └── __init__.py
        ├── application/
        │   ├── __init__.py
        │   ├── services/
        │   │   └── __init__.py
        │   ├── commands/
        │   │   └── __init__.py
        │   └── queries/
        │       └── __init__.py
        ├── infrastructure/
        │   ├── __init__.py
        │   ├── models/
        │   │   └── __init__.py
        │   ├── repositories/
        │   │   └── __init__.py
        │   └── external/
        │       └── __init__.py
        └── presentation/
            ├── __init__.py
            ├── api/
            │   └── __init__.py
            └── schemas/
                └── __init__.py
```

## Step 4: Create Components

Now let's create the actual components. We'll start with a User entity:

### Domain Layer Components

```bash
# Create User entity
fca-scaffold create-component user_management/authentication/domain/entities user

# Create User repository interface
fca-scaffold create-component user_management/authentication/domain/repositories user

# Create value objects
fca-scaffold create-component user_management/authentication/domain/value_objects email
fca-scaffold create-component user_management/authentication/domain/value_objects password
```

### Application Layer Components

```bash
# Create authentication service
fca-scaffold create-component user_management/authentication/application/services auth_service

# Create CQRS commands
fca-scaffold create-component user_management/authentication/application/commands create_user
fca-scaffold create-component user_management/authentication/application/commands login_user

# Create CQRS queries
fca-scaffold create-component user_management/authentication/application/queries get_user
fca-scaffold create-component user_management/authentication/application/queries list_users
```

### Infrastructure Layer Components

```bash
# Create database model
fca-scaffold create-component user_management/authentication/infrastructure/models user

# Create repository implementation
fca-scaffold create-component user_management/authentication/infrastructure/repositories user

# Create external service client
fca-scaffold create-component user_management/authentication/infrastructure/external email_service
```

### Presentation Layer Components

```bash
# Create API router
fca-scaffold create-component user_management/authentication/presentation/api auth

# Create Pydantic schemas
fca-scaffold create-component user_management/authentication/presentation/schemas user
```

## Step 5: Check Project Status

You can check your project's current state at any time:

```bash
fca-scaffold status
```

This shows:
- Project information
- Systems overview
- Module counts
- Creation and update timestamps

## Step 6: Batch Creation (Alternative Approach)

Instead of creating components one by one, you can use batch creation with a YAML specification file:

```bash
# Use the provided example specification
fca-scaffold batch-create examples/components-spec.yaml
```

Or create your own specification file:

```yaml
# my-components.yaml
systems:
  - name: user_management
    modules:
      - name: authentication
        components:
          domain:
            entities: ["user", "role"]
            repositories: ["user", "role"]
            value_objects: ["email", "password"]
          application:
            services: ["auth_service"]
            commands: ["create_user", "login"]
            queries: ["get_user", "list_users"]
          infrastructure:
            models: ["user", "role"]
            repositories: ["user", "role"]
          presentation:
            api: ["auth", "users"]
            schemas: ["user", "auth"]
```

Then run:
```bash
fca-scaffold batch-create my-components.yaml
```

## Step 7: Understanding the Generated Code

Let's look at what was generated:

### Domain Entity (`systems/user_management/authentication/domain/entities/user.py`)

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    """User entity for authentication module."""
    
    id: Optional[str] = Field(None, description="Unique identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # Add your domain-specific fields here
    # Example:
    # email: str = Field(..., description="User email address")
    # username: str = Field(..., description="User username")
    # is_active: bool = Field(True, description="Whether user is active")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Repository Interface (`systems/user_management/authentication/domain/repositories/user_repository.py`)

```python
from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.user import User

class UserRepository(ABC):
    """User repository interface for authentication module."""
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """Save user."""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete user by ID."""
        pass
    
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users with pagination."""
        pass
```

### Application Service (`systems/user_management/authentication/application/services/auth_service_service.py`)

```python
from typing import List, Optional

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository

class AuthServiceService:
    """AuthService application service for authentication module."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def create_user(self, user_data: dict) -> User:
        """Create a new user."""
        user = User(**user_data)
        return await self.user_repository.save(user)
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repository.get_by_id(user_id)
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination."""
        return await self.user_repository.list_all(skip=skip, limit=limit)
    
    async def update_user(self, user_id: str, user_data: dict) -> Optional[User]:
        """Update user."""
        user = await self.user_repository.get_by_id(user_id)
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            return await self.user_repository.save(user)
        return None
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user."""
        return await self.user_repository.delete(user_id)
```

### FastAPI Router (`systems/user_management/authentication/presentation/api/auth_router.py`)

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas.user_schemas import UserResponse, UserCreate, UserUpdate
from ...application.services.auth_service_service import AuthServiceService

router = APIRouter(prefix="/auth", tags=["auth"])

# Dependency injection - you'll need to implement this
def get_auth_service_service() -> AuthServiceService:
    # TODO: Implement dependency injection
    pass

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: AuthServiceService = Depends(get_auth_service_service)
) -> UserResponse:
    """Create a new user."""
    user = await service.create_user(user_data.dict())
    return UserResponse.from_orm(user)

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    service: AuthServiceService = Depends(get_auth_service_service)
) -> List[UserResponse]:
    """List users with pagination."""
    users = await service.list_users(skip=skip, limit=limit)
    return [UserResponse.from_orm(user) for user in users]

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    service: AuthServiceService = Depends(get_auth_service_service)
) -> UserResponse:
    """Get user by ID."""
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    service: AuthServiceService = Depends(get_auth_service_service)
) -> UserResponse:
    """Update user."""
    user = await service.update_user(user_id, user_data.dict(exclude_unset=True))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    service: AuthServiceService = Depends(get_auth_service_service)
) -> None:
    """Delete user."""
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
```

## Step 8: Customization

The generated code provides a solid foundation, but you'll need to customize it for your specific needs:

1. **Add business logic** to your entities and services
2. **Implement dependency injection** in your FastAPI application
3. **Add database connections** and configure your repository implementations
4. **Customize validation** in your Pydantic schemas
5. **Add authentication and authorization** middleware
6. **Configure logging and error handling**

## Step 9: FastAPI Integration and Running Your Application

### Install FastAPI Dependencies

First, install FastAPI and uvicorn if you haven't already:

```bash
# Using pip
pip install fastapi uvicorn[standard]

# Using Poetry
poetry add fastapi uvicorn[standard]
```

### Create the Main FastAPI Application

Use the FastAPI CLI to bootstrap your application:

```bash
# Install FastAPI with all standard dependencies
pip install "fastapi[standard]"

# Or with Poetry
poetry add "fastapi[standard]"

# Create and run a basic FastAPI app (this will create main.py if it doesn't exist)
fastapi dev main.py
```

This command will:
- Create a basic `main.py` file if it doesn't exist
- Start the development server with auto-reload
- Set up the FastAPI application with sensible defaults

Once the basic structure is created, enhance the generated `main.py` with your scaffolded components:

```python
# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from systems.user_management.authentication.presentation.api.auth_router import router as auth_router

# Create FastAPI instance
app = FastAPI(
    title="My Clean Architecture FastAPI App",
    description="A FastAPI application built with clean architecture principles",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware (configure as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper prefixes and tags
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

# Add startup and shutdown events
@app.on_event("startup")
async def startup_event():
    # Initialize database connections, load configurations, etc.
    print("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    # Clean up resources
    print("Application shutting down...")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
```

### Run Your Application

```bash
# Method 1: Run directly with Python
python main.py

# Method 2: Use uvicorn directly (recommended for development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Method 3: Using Poetry (if using Poetry)
poetry run uvicorn main:app --reload
```

### Access Your Application

Once running, your application will be available at:

- **API Base URL**: `http://localhost:8000`
- **Interactive API Documentation**: `http://localhost:8000/docs`
- **Alternative Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

### Next Steps for Production

For production deployment, consider:

1. **Environment Configuration**: Use environment variables for sensitive data
2. **Database Setup**: Configure your database connections in the startup event
3. **Dependency Injection**: Set up proper DI for your repositories and services
4. **Authentication**: Implement JWT or other authentication mechanisms
5. **Logging**: Configure structured logging
6. **Error Handling**: Add global exception handlers
7. **Testing**: Write comprehensive tests for your endpoints

## Advanced Features

### Dry Run Mode

Test what would be created without actually creating files:

```bash
fca-scaffold create-component user_management/authentication/domain/entities product --dry-run
```

### Force Overwrite

Overwrite existing files without confirmation:

```bash
fca-scaffold create-component user_management/authentication/domain/entities user --force
```

### Custom Configuration

Use a custom configuration file:

```bash
fca-scaffold init --config custom-config.yaml
fca-scaffold create-system-context payment --config custom-config.yaml
```

### Configuration Management

```bash
# View current configuration
fca-scaffold config show

# Validate configuration
fca-scaffold config validate

# Check project status
fca-scaffold status
```

## Best Practices

1. **Start with system contexts** - Think about major functional areas first
2. **Keep modules focused** - Each module should have a single responsibility
3. **Follow naming conventions** - Use snake_case for files and PascalCase for classes
4. **Use batch creation** for large projects to save time
5. **Customize templates** if you have specific coding standards
6. **Version control your config** - Include `fca-config.yaml` in your repository
7. **Use dry run mode** to preview changes before applying them

## Next Steps

- Explore the generated code and understand the clean architecture patterns
- Implement your business logic in the domain layer
- Add database models and repository implementations
- Set up dependency injection for your FastAPI application
- Add tests for your components
- Configure CI/CD pipelines
- Deploy your application

Congratulations! You now have a well-structured FastAPI application following clean architecture principles.