# Project Structure

## Overview

The GateGrind V2 backend follows a clean, modern Python application structure that supports the Hexagonal Architecture pattern. The project organization promotes maintainability, testability, and clear separation of concerns.

## Directory Structure

```
gategrind-api/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── api/                      # API layer: routers and controllers
│   │   ├── __init__.py
│   │   ├── dependencies.py       # FastAPI dependencies
│   │   ├── middleware.py         # Custom middleware
│   │   └── v2/                   # V2 API endpoints
│   │       ├── __init__.py
│   │       ├── users.py          # User profile endpoints
│   │       ├── movements.py      # Movement and skill tree endpoints
│   │       ├── progression.py    # Progression and XP endpoints
│   │       ├── awakening.py      # Awakening system endpoints
│   │       ├── dungeons.py       # Dungeon system endpoints
│   │       ├── events.py         # Event logging endpoints
│   │       └── tasks.py          # Async task status endpoints
│   ├── application/              # Application layer: services & background tasks
│   │   ├── __init__.py
│   │   ├── services/             # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── progression_service.py
│   │   │   ├── quest_generation_service.py
│   │   │   ├── dungeon_service.py
│   │   │   ├── awakening_service.py
│   │   │   ├── daily_login_service.py
│   │   │   ├── movement_logging_service.py
│   │   │   └── incursion_service.py
│   │   ├── tasks/                # Background task implementations
│   │   │   ├── __init__.py
│   │   │   ├── dungeon_tasks.py
│   │   │   ├── quest_tasks.py
│   │   │   └── maintenance_tasks.py
│   │   └── dto/                  # Data Transfer Objects
│   │       ├── __init__.py
│   │       ├── profile_dto.py
│   │       ├── skill_tree_dto.py
│   │       └── quest_dto.py
│   ├── core/                     # Core configuration and settings
│   │   ├── __init__.py
│   │   ├── config.py             # Application configuration
│   │   ├── security.py           # Authentication and authorization
│   │   ├── logging.py            # Logging configuration
│   │   └── exceptions.py         # Custom exception classes
│   ├── domain/                   # Domain layer: models and schemas
│   │   ├── __init__.py
│   │   ├── entities/             # Domain entities
│   │   │   ├── __init__.py
│   │   │   ├── ascendant.py
│   │   │   ├── skill_tree.py
│   │   │   ├── quest.py
│   │   │   └── dungeon.py
│   │   ├── schemas/              # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user_schemas.py
│   │   │   ├── movement_schemas.py
│   │   │   ├── quest_schemas.py
│   │   │   └── dungeon_schemas.py
│   │   └── enums/                # Domain enumerations
│   │       ├── __init__.py
│   │       ├── quest_types.py
│   │       ├── stat_types.py
│   │       └── dungeon_types.py
│   └── infrastructure/           # Infrastructure layer: db, cache, etc.
│       ├── __init__.py
│       ├── db/                   # Database configuration and models
│       │   ├── __init__.py
│       │   ├── database.py       # Database connection and session
│       │   ├── models/           # SQLAlchemy models
│       │   │   ├── __init__.py
│       │   │   ├── ascendant.py
│       │   │   ├── stats.py
│       │   │   ├── movements.py
│       │   │   ├── quests.py
│       │   │   └── dungeons.py
│       │   └── migrations/       # Alembic migration files
│       │       ├── env.py
│       │       ├── script.py.mako
│       │       └── versions/
│       ├── repositories/         # Data access layer
│       │   ├── __init__.py
│       │   ├── base_repository.py
│       │   ├── user_repository.py
│       │   ├── movement_repository.py
│       │   ├── quest_repository.py
│       │   └── dungeon_repository.py
│       ├── cache/                # Redis cache implementation
│       │   ├── __init__.py
│       │   ├── cache_service.py
│       │   └── cache_keys.py
│       ├── external/             # External API clients
│       │   ├── __init__.py
│       │   ├── discord_client.py
│       │   └── sentry_client.py
│       └── monitoring/           # Observability and monitoring
│           ├── __init__.py
│           ├── metrics.py
│           └── health_checks.py
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration and fixtures
│   ├── integration/             # Integration tests
│   │   ├── __init__.py
│   │   ├── test_api_endpoints.py
│   │   ├── test_database_operations.py
│   │   └── test_service_integration.py
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_services/
│   │   │   ├── test_progression_service.py
│   │   │   ├── test_quest_generation_service.py
│   │   │   └── test_dungeon_service.py
│   │   ├── test_repositories/
│   │   │   ├── test_user_repository.py
│   │   │   └── test_movement_repository.py
│   │   └── test_domain/
│   │       ├── test_entities.py
│   │       └── test_schemas.py
│   └── fixtures/                # Test data and fixtures
│       ├── __init__.py
│       ├── user_fixtures.py
│       ├── movement_fixtures.py
│       └── quest_fixtures.py
├── scripts/                     # Utility and deployment scripts
│   ├── seed_database.py         # Database seeding script
│   ├── migrate_v1_data.py       # V1 to V2 data migration
│   └── performance_test.py      # Performance testing script
├── docs/                        # Additional documentation
│   ├── api_examples.md
│   ├── deployment_guide.md
│   └── development_setup.md
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── .github/                     # GitHub workflows and templates
│   ├── workflows/
│   │   ├── ci.yaml             # Continuous integration pipeline
│   │   ├── cd.yaml             # Continuous deployment pipeline
│   │   └── security.yaml       # Security scanning workflow
│   └── PULL_REQUEST_TEMPLATE.md
├── alembic.ini                  # Alembic configuration
├── main.py                      # Application entry point
├── pyproject.toml              # Project dependencies and configuration
├── README.md                    # Project documentation
└── requirements.txt             # Python dependencies (generated from pyproject.toml)
```

## Layer Organization

### API Layer (`app/api/`)
**Purpose**: HTTP request handling and response formatting

**Key Files**:
- `v2/users.py`: User profile and authentication endpoints
- `v2/movements.py`: Skill tree and movement library endpoints
- `v2/progression.py`: XP, leveling, and skill unlocking endpoints
- `v2/awakening.py`: Daily awakening and quest generation endpoints
- `v2/dungeons.py`: Dungeon entry and completion endpoints
- `v2/events.py`: Movement logging and event tracking endpoints
- `dependencies.py`: FastAPI dependency injection setup
- `middleware.py`: Custom middleware for logging, CORS, etc.

### Application Layer (`app/application/`)
**Purpose**: Business logic orchestration and use case implementation

**Key Components**:
- **Services**: Core business logic implementation
- **Tasks**: Background job processing
- **DTOs**: Data transfer objects for API responses

**Service Organization**:
- `progression_service.py`: XP, leveling, and Aura calculations
- `quest_generation_service.py`: Universal quest generation engine
- `dungeon_service.py`: Dungeon mechanics and progression
- `awakening_service.py`: Daily ritual and quest management
- `daily_login_service.py`: Login rewards and streak tracking

### Domain Layer (`app/domain/`)
**Purpose**: Core business entities and rules

**Key Components**:
- **Entities**: Pure business objects with behavior
- **Schemas**: Pydantic models for validation and serialization
- **Enums**: Domain-specific enumerations and constants

**Entity Organization**:
- `ascendant.py`: User profile and progression logic
- `skill_tree.py`: Skill tree structure and unlocking rules
- `quest.py`: Quest generation and completion logic
- `dungeon.py`: Dungeon mechanics and trial generation

### Infrastructure Layer (`app/infrastructure/`)
**Purpose**: External system integration and technical concerns

**Key Components**:
- **Database**: SQLAlchemy models and database configuration
- **Repositories**: Data access patterns and query optimization
- **Cache**: Redis integration for performance optimization
- **External**: Third-party API clients and integrations
- **Monitoring**: Observability and health checking

## Configuration Management

### Environment Configuration (`app/core/config.py`)
```python
from pydantic import BaseSettings, ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")
    
    # Database
    database_url: str
    database_pool_size: int = 10
    
    # Redis
    redis_url: str
    redis_ttl_default: int = 300
    
    # Security
    secret_key: str
    discord_client_id: str
    discord_client_secret: str
    
    # Monitoring
    sentry_dsn: str
    log_level: str = "INFO"
    
    # Feature flags
    enable_async_dungeons: bool = True
    enable_daily_login_rewards: bool = True
```

### Development vs Production
- **Development**: Local database, debug logging, hot reload
- **Testing**: In-memory database, mock external services
- **Production**: Managed database, structured logging, monitoring

## Testing Organization

### Test Structure
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Fixtures**: Reusable test data and setup

### Test Configuration (`tests/conftest.py`)
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.db.database import get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db_session():
    # Test database session setup
    pass

@pytest.fixture
def sample_user():
    # Sample user data for testing
    pass
```

## Build and Deployment

### Dependencies (`pyproject.toml`)
```toml
[tool.poetry]
name = "gategrind-api"
version = "2.0.0"
description = "GateGrind V2 Backend API"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
sqlalchemy = "^2.0.0"
pydantic = "^2.0.0"
redis = "^5.0.0"
pytest = "^7.0.0"

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.black]
line-length = 88
target-version = ['py311']
```

### Docker Configuration
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Development Workflow

### Local Development Setup
1. Clone repository
2. Install dependencies: `poetry install`
3. Set up environment variables: `cp .env.example .env`
4. Run database migrations: `alembic upgrade head`
5. Seed database: `python scripts/seed_database.py`
6. Start development server: `uvicorn main:app --reload`

### Code Quality Checks
```bash
# Formatting
black app/ tests/

# Linting
ruff app/ tests/

# Type checking
mypy app/

# Testing
pytest tests/ --cov=app
```

### Git Workflow
1. Feature branches from `main`
2. Pull request with automated checks
3. Code review and approval
4. Merge to `main` triggers deployment

---
*This project structure provides a solid foundation for scalable, maintainable, and testable Python application development following modern best practices.*