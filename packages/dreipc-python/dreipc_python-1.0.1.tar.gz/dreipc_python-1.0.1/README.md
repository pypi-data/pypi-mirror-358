# DreiPC Python CLI

A simple command-line tool for creating FastAPI projects

## Installation

### From PyPI (when published)
```bash
pip install dreipc-python
```

### From Source
```bash
git clone https://github.com/yourusername/dreipc-python.git
cd dreipc-python
pip install -e .
```

## Usage

### Create a new project
```bash
dreipc-python create my-awesome-api
```

### Interactive mode
```bash
dreipc-python create my-api --interactive
```

### With custom details
```bash
dreipc-python create my-api \
  --author "Your Name" \
  --email "your@email.com" \
  --description "My awesome FastAPI application"
```

### Get help
```bash
dreipc-python --help
dreipc-python create --help
```

## Generated Project Features

✅ **FastAPI** with async/await support  
✅ **Dependency Injection** using dependency-injector  
✅ **Pydantic Models** for data validation  
✅ **Structured Layout** with separation of concerns  
✅ **Testing Suite** with pytest and pytest-asyncio  
✅ **Code Quality** tools (Black, isort, flake8, mypy)  
✅ **Poetry** for dependency management  
✅ **Docker** support with Dockerfile  
✅ **Makefile** with common development tasks  
✅ **Environment Configuration** with pydantic-settings  
✅ **CORS Middleware** preconfigured  
✅ **API Documentation** with FastAPI's built-in Swagger UI  

## Generated Project Structure

```
my-awesome-api/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── health.py      # Health check endpoints
│   │   │   └── users.py       # User CRUD endpoints
│   │   └── routes.py          # API router configuration
│   ├── core/
│   │   ├── config.py          # Application settings
│   │   └── container.py       # DI container setup
│   ├── dependencies/
│   │   └── container.py       # FastAPI dependencies
│   ├── models/
│   │   └── user.py            # Pydantic models
│   ├── services/
│   │   ├── base.py            # Base service class
│   │   └── user_service.py    # Business logic
│   └── main.py                # Application entry point
├── tests/
│   ├── unit/
│   │   └── test_user_service.py
│   ├── integration/
│   │   └── test_api.py
│   └── conftest.py
├── pyproject.toml             # Poetry configuration
├── Dockerfile                 # Docker configuration
├── Makefile                   # Development commands
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

## Quick Start After Project Creation

1. **Navigate to your project:**
   ```bash
   cd my-awesome-api
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

4. **Run the application:**
   ```bash
   make run
   # or
   poetry run uvicorn app.main:app --reload
   ```

5. **Visit the API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Available Make Commands

- `make run` - Start the development server
- `make test` - Run tests
- `make test-cov` - Run tests with coverage report
- `make format` - Format code (Black + isort)
- `make lint` - Lint code (flake8 + mypy)
- `make clean` - Remove cache files
- `make build` - Build the package
- `make docker-build` - Build Docker image
- `make docker-run` - Run Docker container

## Example API Usage

The generated project includes a complete user management API:

### Create a user
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

### Get all users
```bash
curl "http://localhost:8000/api/v1/users/"
```

### Get a specific user
```bash
curl "http://localhost:8000/api/v1/users/1"
```

### Update a user
```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe"}'
```

### Delete a user
```bash
curl -X DELETE "http://localhost:8000/api/v1/users/1"
```

## Requirements

- Python 3.8+
- Poetry (for dependency management)

## Development

To contribute to this project:

1. Clone the repository
2. Install development dependencies: `pip install -e .[dev]`
3. Run tests: `pytest`
4. Format code: `black . && isort .`
5. Lint code: `flake8 && mypy fastapi_cli/`

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.