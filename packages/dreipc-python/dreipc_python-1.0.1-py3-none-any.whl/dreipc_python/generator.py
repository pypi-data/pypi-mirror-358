"""Simple FastAPI project generator."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class FastAPIProjectGenerator:
    """Generate simple FastAPI projects with dependency injection."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_name = config["project_name"]
        self.project_dir = Path.cwd() / self.project_name
    
    def create_project(self) -> None:
        """Create the complete FastAPI project."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Create project structure
            task = progress.add_task("Creating project structure...", total=None)
            self._create_directory_structure()
            progress.update(task, description="✅ Project structure created")
            
            # Create configuration files
            task = progress.add_task("Creating configuration files...", total=None)
            self._create_config_files()
            progress.update(task, description="✅ Configuration files created")
            
            # Create application files
            task = progress.add_task("Creating application files...", total=None)
            self._create_app_files()
            progress.update(task, description="✅ Application files created")
            
            # Create tests
            task = progress.add_task("Creating tests...", total=None)
            self._create_tests()
            progress.update(task, description="✅ Tests created")
            
            # Install dependencies
            task = progress.add_task("Installing dependencies...", total=None)
            self._install_dependencies()
            progress.update(task, description="✅ Dependencies installed")
    
    def _create_directory_structure(self) -> None:
        """Create the project directory structure."""
        directories = [
            "app/api/endpoints",
            "app/core",
            "app/models",
            "app/services",
            "app/dependencies",
            "tests/unit",
            "tests/integration",
        ]
        
        # Create directories
        self.project_dir.mkdir(exist_ok=True)
        for directory in directories:
            (self.project_dir / directory).mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py files for Python packages
            if directory.startswith(("app/", "tests/")):
                (self.project_dir / directory / "__init__.py").touch()
    
    def _create_config_files(self) -> None:
        """Create configuration files."""
        # pyproject.toml
        (self.project_dir / "pyproject.toml").write_text(self._get_pyproject_toml())
        
        # .env.example
        (self.project_dir / ".env.example").write_text(self._get_env_example())
        
        # .gitignore
        (self.project_dir / ".gitignore").write_text(self._get_gitignore())
        
        # README.md
        (self.project_dir / "README.md").write_text(self._get_readme())
        
        # Makefile
        (self.project_dir / "Makefile").write_text(self._get_makefile())
        
        # Dockerfile
        (self.project_dir / "Dockerfile").write_text(self._get_dockerfile())
    
    def _create_app_files(self) -> None:
        """Create application files."""
        app_files = {
            "app/main.py": self._get_main_py(),
            "app/core/config.py": self._get_config_py(),
            "app/core/container.py": self._get_container_py(),
            "app/dependencies/container.py": self._get_dependencies_py(),
            "app/models/user.py": self._get_user_model(),
            "app/services/base.py": self._get_base_service(),
            "app/services/user_service.py": self._get_user_service(),
            "app/api/routes.py": self._get_api_routes(),
            "app/api/endpoints/health.py": self._get_health_endpoint(),
            "app/api/endpoints/users.py": self._get_users_endpoint(),
        }
        
        for filepath, content in app_files.items():
            file_path = self.project_dir / filepath
            file_path.write_text(content)
    
    def _create_tests(self) -> None:
        """Create test files."""
        test_files = {
            "tests/conftest.py": self._get_conftest(),
            "tests/unit/test_user_service.py": self._get_user_service_test(),
            "tests/integration/test_api.py": self._get_api_test(),
        }
        
        for filepath, content in test_files.items():
            file_path = self.project_dir / filepath
            file_path.write_text(content)
    
    def _install_dependencies(self) -> None:
        """Install Poetry dependencies."""
        try:
            original_cwd = os.getcwd()
            os.chdir(self.project_dir)
            
            subprocess.run(
                ["poetry", "install"],
                check=True,
                capture_output=True,
                text=True,
            )
                
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]Warning: Failed to install dependencies: {e}[/yellow]")
            console.print("[yellow]You can install them manually by running 'poetry install'[/yellow]")
        except FileNotFoundError:
            console.print("[yellow]Warning: Poetry not found. Please install Poetry first.[/yellow]")
            console.print("[yellow]Visit: https://python-poetry.org/docs/#installation[/yellow]")
        finally:
            os.chdir(original_cwd)
    
    # Template methods
    def _get_pyproject_toml(self) -> str:
        """Get pyproject.toml template."""
        return f'''[tool.poetry]
name = "{self.project_name}"
version = "0.1.0"
description = "{self.config['description']}"
authors = ["{self.config['author']} <{self.config['email']}>"]
readme = "README.md"
packages = [{{include = "app"}}]

[tool.poetry.dependencies]
python
fastapi
uvicorn = {{extras = ["standard"]}}
pydantic 
pydantic-settings 
python-multipart 
httpx 
dependency-injector 

[tool.poetry.group.dev.dependencies]
pytest 
pytest-asyncio 
pytest-cov 
black 
isort 
flake8
mypy 

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["app"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=app --cov-report=term-missing"
asyncio_mode = "auto"
'''

    def _get_main_py(self) -> str:
        """Get main.py template."""
        return '''"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.container import Container


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    container = Container()
    container.wire(modules=[
        "app.api.routes", 
        "app.api.endpoints.health",
        "app.api.endpoints.users",
    ])
    app.container = container
    
    yield
    
    # Shutdown
    await container.shutdown_resources()


def create_application() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
'''

    def _get_config_py(self) -> str:
        """Get config.py template."""
        return f'''"""Application configuration."""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    PROJECT_NAME: str = "{self.project_name}"
    PROJECT_DESCRIPTION: str = "{self.config['description']}"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-this")
    
    # External APIs
    EXTERNAL_API_URL: str = Field(default="https://api.example.com")
    EXTERNAL_API_KEY: str = Field(default="")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
'''

    def _get_container_py(self) -> str:
        """Get container.py template."""
        return '''"""Dependency injection container."""

import httpx
from dependency_injector import containers, providers

from app.core.config import settings
from app.services.user_service import UserService


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""
    
    # Configuration
    config = providers.Configuration()
    
    # HTTP Client
    http_client = providers.Resource(
        httpx.AsyncClient,
        timeout=30.0,
    )
    
    # Services
    user_service = providers.Factory(
        UserService,
        http_client=http_client,
        api_url=settings.EXTERNAL_API_URL,
        api_key=settings.EXTERNAL_API_KEY,
    )
    
    async def shutdown_resources(self) -> None:
        """Shutdown container resources."""
        if hasattr(self, 'http_client') and self.http_client.provided:
            await self.http_client.provided.aclose()
'''

    def _get_dependencies_py(self) -> str:
        """Get dependencies.py template."""
        return '''"""Container dependencies."""

from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from app.core.container import Container
from app.services.user_service import UserService


@inject
def get_user_service(
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserService:
    """Get user service dependency."""
    return user_service
'''

    def _get_user_model(self) -> str:
        """Get user model template."""
        return '''"""User models."""

from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user model."""
    name: str
    email: EmailStr


class UserCreate(UserBase):
    """User creation model."""
    pass


class UserUpdate(BaseModel):
    """User update model."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase):
    """User model."""
    id: int
    is_active: bool = True
    
    class Config:
        from_attributes = True


class UserResponse(User):
    """User response model."""
    pass
'''

    def _get_base_service(self) -> str:
        """Get base service template."""
        return '''"""Base service class."""

from abc import ABC
from typing import Any, Dict


class BaseService(ABC):
    """Base service class."""
    
    def __init__(self) -> None:
        """Initialize service."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the service."""
        return {"status": "healthy", "service": self.__class__.__name__}
'''

    def _get_user_service(self) -> str:
        """Get user service template."""
        return '''"""User service."""

from typing import Any, Dict, List, Optional

import httpx

from app.models.user import User, UserCreate, UserUpdate
from app.services.base import BaseService


class UserService(BaseService):
    """User service with business logic."""
    
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        api_url: str,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize user service."""
        super().__init__()
        self.http_client = http_client
        self.api_url = api_url
        self.api_key = api_key
        self._users: Dict[int, User] = {}
        self._next_id = 1
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        user = User(
            id=self._next_id,
            name=user_data.name,
            email=user_data.email,
            is_active=True,
        )
        self._users[user.id] = user
        self._next_id += 1
        
        # Example: Log user creation (could call external API here)
        print(f"User created: {user.name} ({user.email})")
        
        return user
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        users = list(self._users.values())
        return users[skip : skip + limit]
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        if user_id not in self._users:
            return None
        
        user = self._users[user_id]
        if user_data.name is not None:
            user.name = user_data.name
        if user_data.email is not None:
            user.email = user_data.email
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
'''

    def _get_api_routes(self) -> str:
        """Get API routes template."""
        return '''"""API routes."""

from fastapi import APIRouter

from app.api.endpoints import health, users

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
'''

    def _get_health_endpoint(self) -> str:
        """Get health endpoint template."""
        return '''"""Health check endpoints."""

from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "FastAPI App",
        "version": "0.1.0",
    }
'''

    def _get_users_endpoint(self) -> str:
        """Get users endpoint template."""
        return '''"""User endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.container import get_user_service
from app.models.user import User, UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Create a new user."""
    user = await user_service.create_user(user_data)
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get user by ID."""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(user)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
) -> List[UserResponse]:
    """Get all users."""
    users = await user_service.get_users(skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Update user."""
    user = await user_service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
) -> None:
    """Delete user."""
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
'''

    # Configuration file templates
    def _get_env_example(self) -> str:
        """Get .env.example template."""
        return f'''# Application Configuration
PROJECT_NAME="{self.project_name}"
PROJECT_DESCRIPTION="{self.config['description']}"
VERSION="0.1.0"
API_V1_STR="/api/v1"

# CORS
ALLOWED_HOSTS=["*"]

# Security
SECRET_KEY="your-secret-key-change-this"

# External APIs
EXTERNAL_API_URL="https://api.example.com"
EXTERNAL_API_KEY=""

# Logging
LOG_LEVEL="INFO"
'''

    def _get_gitignore(self) -> str:
        """Get .gitignore template."""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/
.nox/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
'''

    def _get_readme(self) -> str:
        """Get README.md template."""
        return f'''# {self.project_name}

{self.config['description']}

## Features

- FastAPI with async/await support
- Dependency injection using dependency-injector
- Pydantic models for data validation
- Structured project layout
- Unit and integration tests
- Code formatting and linting tools
- Poetry for dependency management

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Run the application:
```bash
poetry run uvicorn app.main:app --reload
```

## Development Guideline

### Setup your Environment

1. **Python**: Install required Python version using  [pyenv](https://github.com/pyenv/pyenv)  (Linux | Mac)
   or [pyenv-win](https://github.com/pyenv-win/pyenv-win) (Windows)
2. **Poetry**: Make sure [Poetry](https://python-poetry.org/) is properly installed by checking `poetry` command inside
   your Terminal of choice
3. **uv**: Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
3. **Dependencies**: Install all (including dev) dependencies `poetry install --with dev` or `uv sync`
4. **git pre-commit hooks**: Install all pre commit hooks using `poetry run pre-commit install`. This Step can be
   skipped if you installed the [pre-commit poetry plugin](https://pypi.org/project/poetry-pre-commit-plugin/)

### Dependencies

All dependencies are managed through **one** file: `./pyproject.toml`

Please be aware that you run `poetry update` after changing something on the dependencies.

### Git

As our default SCM System we use Git. All Development Processes are based on this central piece of Code versioning.
To make it more readable and better to understand for all of us we force all developers to use
the [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/) pattern
in their commit messages. Additionally, we are able to auto-calculate **version** our software. We
use [Semantic Versioning](https://semver.org/)

#### pre-commit hooks

Some development tasks like **code-formatting**, **optimize imports** and **git commit message linting** are setup to
to remove unnecessary ci round trips and frustrations due to forgotten code formatting etc. before the code pushed to
the server.
These things are optional and can be deactivated during development on your local machine.

To see what's happening please check the `.pre-commit-config.yaml` config or the local `.git/hooks/` folder for more
details.

Keep in mind that those checks are done in ci!

### Run Code Quality

- test the code: `poetry run pytest`
- format-code: `poetry run black .`
- optimize imports: `poetry run isort .`

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Requirements

- [Python](https://www.python.org/) (using [pyenv](https://github.com/pyenv/pyenv))
- [Poetry](https://python-poetry.org/)
- [Git](https://git-scm.com/)

```
'''

    def _get_makefile(self) -> str:
        """Get Makefile template."""
        return f'''.PHONY: install run test format lint clean help

install:
	poetry install

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	poetry run pytest -v

test-cov:
	poetry run pytest --cov=app --cov-report=html --cov-report=term-missing

format:
	poetry run black .
	poetry run isort .

lint:
	poetry run flake8 app/ tests/
	poetry run mypy app/

clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

build:
	poetry build

docker-build:
	docker build -t {self.project_name} .

docker-run:
	docker run -p 8000:8000 {self.project_name}

help:
	@echo "Available commands:"
	@echo "  install      Install dependencies"
	@echo "  run          Run the development server"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  format       Format code with black and isort"
	@echo "  lint         Lint code with flake8 and mypy"
	@echo "  clean        Remove cache files"
	@echo "  build        Build package"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run Docker container"
'''

    def _get_dockerfile(self) -> str:
        """Get Dockerfile template."""
        return '''FROM python:3.11-slim

WORKDIR /app

# Install Poetry
ENV POETRY_HOME="/opt/poetry" \\
    POETRY_CACHE_DIR=/opt/poetry/cache \\
    POETRY_VENV_IN_PROJECT=1 \\
    POETRY_NO_INTERACTION=1

RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --only=main --no-root

# Copy application
COPY . .

# Install application
RUN poetry install --only=main

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

    # Test file templates
    def _get_conftest(self) -> str:
        """Get conftest.py template."""
        return '''"""Test configuration."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_application


@pytest.fixture
def client():
    """Test client fixture."""
    app = create_application()
    return TestClient(app)


@pytest.fixture
def mock_user_data():
    """Mock user data fixture."""
    return {
        "name": "John Doe",
        "email": "john@example.com",
    }
'''

    def _get_user_service_test(self) -> str:
        """Get user service test template."""
        return '''"""Unit tests for user service."""

import pytest
import httpx

from app.models.user import UserCreate
from app.services.user_service import UserService


@pytest.fixture
def user_service():
    """User service fixture."""
    http_client = httpx.AsyncClient()
    return UserService(
        http_client=http_client,
        api_url="https://api.example.com",
        api_key="test-key"
    )


@pytest.mark.asyncio
async def test_create_user(user_service):
    """Test user creation."""
    user_data = UserCreate(name="John Doe", email="john@example.com")
    user = await user_service.create_user(user_data)
    
    assert user.id == 1
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_get_user(user_service):
    """Test getting user by ID."""
    user_data = UserCreate(name="Jane Doe", email="jane@example.com")
    created_user = await user_service.create_user(user_data)
    
    retrieved_user = await user_service.get_user(created_user.id)
    
    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.name == "Jane Doe"


@pytest.mark.asyncio
async def test_get_nonexistent_user(user_service):
    """Test getting non-existent user."""
    user = await user_service.get_user(999)
    assert user is None


@pytest.mark.asyncio
async def test_update_user(user_service):
    """Test updating user."""
    from app.models.user import UserUpdate
    
    user_data = UserCreate(name="Bob Smith", email="bob@example.com")
    created_user = await user_service.create_user(user_data)
    
    update_data = UserUpdate(name="Bob Johnson")
    updated_user = await user_service.update_user(created_user.id, update_data)
    
    assert updated_user is not None
    assert updated_user.name == "Bob Johnson"
    assert updated_user.email == "bob@example.com"  # Email unchanged


@pytest.mark.asyncio
async def test_delete_user(user_service):
    """Test deleting user."""
    user_data = UserCreate(name="Alice Brown", email="alice@example.com")
    created_user = await user_service.create_user(user_data)
    
    # Delete user
    success = await user_service.delete_user(created_user.id)
    assert success is True
    
    # Verify user is deleted
    retrieved_user = await user_service.get_user(created_user.id)
    assert retrieved_user is None


@pytest.mark.asyncio
async def test_get_users_pagination(user_service):
    """Test getting users with pagination."""
    # Create multiple users
    for i in range(5):
        user_data = UserCreate(name=f"User {i}", email=f"user{i}@example.com")
        await user_service.create_user(user_data)
    
    # Test pagination
    users_page1 = await user_service.get_users(skip=0, limit=3)
    assert len(users_page1) == 3
    
    users_page2 = await user_service.get_users(skip=3, limit=3)
    assert len(users_page2) == 2
'''

    def _get_api_test(self) -> str:
        """Get API integration test template."""
        return '''"""Integration tests for API endpoints."""

import pytest


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "FastAPI App"


def test_create_user(client, mock_user_data):
    """Test user creation endpoint."""
    response = client.post("/api/v1/users/", json=mock_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == mock_user_data["name"]
    assert data["email"] == mock_user_data["email"]
    assert "id" in data
    assert data["is_active"] is True


def test_get_user(client, mock_user_data):
    """Test get user endpoint."""
    # Create user first
    create_response = client.post("/api/v1/users/", json=mock_user_data)
    user_id = create_response.json()["id"]
    
    # Get user
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == mock_user_data["name"]
    assert data["email"] == mock_user_data["email"]


def test_get_nonexistent_user(client):
    """Test getting non-existent user."""
    response = client.get("/api/v1/users/999")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


def test_update_user(client, mock_user_data):
    """Test update user endpoint."""
    # Create user first
    create_response = client.post("/api/v1/users/", json=mock_user_data)
    user_id = create_response.json()["id"]
    
    # Update user
    update_data = {"name": "Jane Smith"}
    response = client.put(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Smith"
    assert data["email"] == mock_user_data["email"]  # Email unchanged


def test_delete_user(client, mock_user_data):
    """Test delete user endpoint."""
    # Create user first
    create_response = client.post("/api/v1/users/", json=mock_user_data)
    user_id = create_response.json()["id"]
    
    # Delete user
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 204
    
    # Verify user is deleted
    get_response = client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 404


def test_get_users_list(client):
    """Test get users list endpoint."""
    # Create a few users
    for i in range(3):
        user_data = {"name": f"User {i}", "email": f"user{i}@example.com"}
        client.post("/api/v1/users/", json=user_data)
    
    # Get users list
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert all("id" in user and "name" in user and "email" in user for user in data)


def test_get_users_pagination(client):
    """Test users list pagination."""
    # Create multiple users
    for i in range(5):
        user_data = {"name": f"User {i}", "email": f"user{i}@example.com"}
        client.post("/api/v1/users/", json=user_data)
    
    # Test pagination
    response = client.get("/api/v1/users/?skip=0&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3


def test_create_user_invalid_email(client):
    """Test creating user with invalid email."""
    invalid_data = {"name": "Test User", "email": "invalid-email"}
    response = client.post("/api/v1/users/", json=invalid_data)
    assert response.status_code == 422  # Validation error
'''