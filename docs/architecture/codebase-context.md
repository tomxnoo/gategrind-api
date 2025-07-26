# RoS-TRAE Codebase Context for BMad V2 Agents

## Project Overview: BMad-Method Universal AI Agent Framework
**RoS-TRAE** (Realm of Shadows - Training, Raids, and Exploration) is a comprehensive fitness gamification platform that serves as both a Discord bot and FastAPI backend. This project demonstrates the **BMad-Method: Universal AI Agent Framework** with two key innovations:

1. **Agentic Planning**: AI agents that understand project context and execute complex workflows
2. **Context-Engineered Development**: Structured documentation and templates that enable AI agents to work effectively

### Project Status: GateGrind V2 - "Brownfield x Greenfield" Migration
The project is currently implementing **GateGrind V2**, a strategic "Brownfield x Greenfield" approach that combines:
- **New V2 Game Systems**: Awakening, Dungeons, Skill Tree, Aura systems
- **Re-implemented V1 Features**: Movement Logging, XP Engine, Incursions
- **Single Authoritative API**: Unified game mechanics through FastAPI
- **Dual-Path Progression**: Supporting both existing and new progression systems

## ⚠️ CRITICAL: V1/V2 Mixed Architecture (Migration in Progress)

### V2 Components Locations

V2 components are organized in their dedicated directory structures:

- **V2 Schemas**: `/app/api/v2/schemas/` (Pydantic request/response models)
- **V2 Models**: `/app/infrastructure/database/models/v2/` (SQLAlchemy database models)
- **V2 Services**: `/app/application/services/` (Business logic layer, shared between V1/V2)
- **V2 API Endpoints**: `/app/api/v2/` (FastAPI routers and endpoints)

### V2 Implementation Details

#### Database Schema & Models
- **10 V2 Tables**: Ascendant, SkillTreeNode, Quest, QuestCompletion, DungeonKey, DungeonProgress, UserSkillProgress, Movement, MovementCategory, MovementProgression
- **Models Location**: `/app/infrastructure/database/models/v2/`
- **Migration**: Alembic migration `f635a66fc269_initial_v2_schema_migration.py`
- **Test Coverage**: 93% coverage standard for all V2 models

#### XP Engine & Progression System
- **Level-up Formula**: `100 * (current_level ^ 1.5)`
- **XP Categories**: 'global', 'strength', 'endurance', 'technique'
- **Stat Points**: +1 to each stat on level-up
- **XP Distribution**: 75% of global XP goes to relevant stat-specific category
- **Service**: `ProgressionService.add_xp(user_id, amount, category)`

#### Aura Calculation System
```python
total_aura = base_aura + stat_bonus + skill_bonus + achievement_bonus
```
- **Base Aura**: User's current aura value
- **Stat Bonus**: Calculated from user's stat levels
- **Skill Bonus**: From unlocked skill tree nodes
- **Achievement Bonus**: From completed quests/milestones

#### Milestone Progression System
- **Default Interval**: 150 stat points per milestone
- **Thresholds**: 150, 300, 450, 600, 750, etc.
- **Rewards**: +1 stat point per milestone achieved
- **Multi-Milestone**: Can achieve multiple milestones in single XP gain

#### Movement Logging & XP Calculation
- **XP Formula**: `reps * movement.xp_per_rep`
- **Endpoint**: `POST /v2/events/log-movement`
- **Response**: Updated user stats, level, and aura
- **Service**: `MovementLoggingService` handles exercise tracking

#### Database Seeding
- **Movement Categories**: 6 categories seeded
- **Skill Tree Nodes**: 90 nodes (5 levels × 18 V2 categories)
- **Movement Progressions**: 239 progressions seeded
- **Idempotent**: Seeding scripts can be run multiple times safely

#### Service Layer Patterns
- **Base Class**: All services inherit from `BaseService`
- **Dependency Injection**: Services injected via FastAPI dependencies
- **Transaction Management**: Database sessions managed at service level
- **Error Handling**: Standardized exception handling across services

### V1 Components (Legacy - Avoid for New Development)
- **Discord Bot**: `/features/`, `/cogs/` - V1 Discord.py modules
- **API Routes**: `/api/routes/` - V1 FastAPI routes  
- **Models**: `/api/models/`, `/core/database/models/` - V1 SQLAlchemy models
- **Core Utils**: `/core/` - V1 shared utilities

### V2 Components (Use for New Development)
- **API Routes**: `/app/api/v2/` - V2 FastAPI endpoints
- **Models**: `/app/infrastructure/database/models/v2/` - V2 SQLAlchemy models
- **Services**: `/app/application/services/` - V2 business logic
- **Repositories**: `/app/infrastructure/repositories/` - V2 data access

## Flattened Codebase Reference
- **Total Files**: ~500+ files across Discord bot, FastAPI backend, database models, and testing infrastructure
- **Primary Languages**: Python (Discord.py, FastAPI, SQLAlchemy), JavaScript (tooling)
- **Architecture**: Hexagonal/Clean Architecture with V2 migration in progress

## Project Architecture

### Core Components
1. **Discord Bot** (`/features`, `/cogs`) - V1 Discord.py bot with feature modules
2. **FastAPI Backend** (`/api`, `/app`) - REST API with V1 and V2 endpoints
3. **Database Layer** (`/core/database`, `/app/infrastructure`) - SQLAlchemy models and repositories
4. **Testing Infrastructure** (`/tests`) - Comprehensive test suite
5. **Tooling** (`/tools`) - Build, deployment, and development utilities

### Key Directories
- `/api/` - V1 FastAPI application and routes (+ V2 schemas during migration)
- `/app/` - V2 application following hexagonal architecture
- `/features/` - V1 Discord bot feature modules
- `/core/` - V1 shared utilities and database
- `/tests/` - Test suites for both V1 and V2
- `/docs/` - Architecture documentation and stories
- `/scripts/` - Database seeding and utility scripts

### Technology Stack (Definitive)
- **Backend Framework**: FastAPI (Python 3.11+)
- **Database**: NeonDB (PostgreSQL) with connection pooling
- **ORM**: SQLAlchemy 2.0+ with async support
- **Testing**: Pytest with comprehensive fixtures and 80% coverage target
- **Discord Integration**: Discord.py for bot functionality
- **Caching**: Redis for performance optimization
- **Migrations**: Alembic for database schema management
- **Observability**: Sentry for error tracking and monitoring
- **Deployment**: Docker containers with Fly.io hosting
- **Development**: Hexagonal (Ports and Adapters) architecture

### Architectural Enhancements
- **Async-First Design**: All database operations and external API calls use async/await
- **Repository Pattern**: Clean separation between business logic and data access
- **Service Layer**: Centralized business logic with dependency injection
- **Schema Validation**: Pydantic models for request/response validation
- **Error Handling**: Comprehensive exception handling with Sentry integration
- **Performance**: Connection pooling, caching, and optimized queries

## Development Patterns

### Database Patterns
- **V1**: Direct SQLAlchemy models in `/core/database/models/`
- **V2**: Repository pattern in `/app/infrastructure/repositories/`
- **Migrations**: Alembic for schema changes
- **Seeding**: Scripts in `/scripts/` for test data

### Testing Infrastructure (Comprehensive)
- **Location**: `/tests/` with comprehensive fixtures and configuration
- **Structure**:
  - `conftest.py` - Pytest configuration and shared fixtures
  - `test_models_v2.py` - Unit tests for V2 database models
  - **Awakening System Tests**: Comprehensive test suite for awakening mechanics
  - **Movement System Tests**: Tests for movement logging and validation
  - **API Tests**: Integration tests for FastAPI endpoints
  - **Service Tests**: Unit tests for business logic services

#### Testing Standards & Guidelines
- **Coverage Target**: 80% minimum test coverage
- **Test Types**: Unit tests, integration tests, API endpoint tests
- **Database Testing**: Isolated test database with automatic cleanup
- **Async Testing**: Proper async/await patterns with `pytest-asyncio`
- **Mocking Strategy**: Comprehensive mocking of external dependencies

#### Critical Testing Patterns
**✅ CORRECT Async Mocking Patterns:**
```python
# Correct AsyncMock usage
mock_service = AsyncMock(spec=AwakeningService)
mock_service.create_awakening.return_value = expected_result

# Correct execute_in_transaction mocking
mock_execute = AsyncMock()
mock_execute.return_value = expected_result
```

**❌ AVOID These Common Mistakes:**
- Mixing real services with partial mocking
- Using wrong service references in tests
- Forgetting to mock `execute_in_transaction`
- Mock type mismatches (using `Mock` instead of `AsyncMock`)
- Missing mock attributes for service methods

#### Mocking Checklist for New Tests
- [ ] Use `AsyncMock` for all async services and methods
- [ ] Mock `execute_in_transaction` when testing database operations
- [ ] Specify `spec` parameter for type safety
- [ ] Set up return values for all called methods
- [ ] Verify mock calls with proper assertions
- [ ] Use proper async test fixtures from `conftest.py`

#### Test File Examples (Working References)
- `tests/test_models_v2.py` - V2 model testing patterns
- `tests/test_awakening_service.py` - Service layer testing
- `tests/test_api_v2_endpoints.py` - API endpoint testing

### Feature Modularity
- **V1 Discord Features**: Self-contained modules in `/features/`
- **V2 API Features**: Clean architecture in `/app/`
- **Shared Logic**: Business services in `/app/application/services/`

### Integration Points
- **Discord ↔ API**: Shared database models and utilities
- **V1 ↔ V2**: V1 FastAPI app includes V2 router for compatibility
- **Caching**: Redis for performance optimization

## BMad Method Framework Integration

### Core BMad Components
The project implements the **BMad Method** as an AI agent framework with these core components:

#### 1. Agents (AI Personas)
- **Developer Agent**: Full-stack implementation specialist
- **Architect Agent**: System design and technical architecture
- **Product Manager Agent**: Requirements and story management
- **Scrum Master Agent**: Story validation and workflow management
- **Analyst Agent**: Project analysis and documentation

#### 2. Agent Teams
- **Team IDE Minimal**: Core development team for IDE-based work
- **Team Fullstack**: Complete fullstack development capabilities
- **Team No-UI**: Backend-focused development team

#### 3. Workflows & Resources
- **Templates**: Reusable document templates (PRD, architecture, stories)
- **Tasks**: Executable workflow instructions for agents
- **Checklists**: Quality assurance and validation checklists
- **Data**: Shared data resources and configurations

#### 4. Build & Delivery Process
- **IDE Integration**: Native integration with development environments
- **Web UI**: Browser-based interface for agent collaboration
- **Planning Workflows**: Structured approach to project planning
- **Core Development**: Implementation and testing workflows

### BMad Configuration
- **Configuration File**: `.bmad-core/core-config.yaml`
- **Story Location**: `docs/stories/`
- **Architecture Docs**: `docs/architecture/` (sharded)
- **PRD Documents**: `docs/prd/` (sharded)
- **Debug Logging**: `.ai/debug-log.md`

### Development Workflow (BMad Method)
1. **Story Creation**: Product Manager creates detailed user stories
2. **Architecture Review**: Architect validates technical approach
3. **Implementation**: Developer executes story tasks sequentially
4. **Testing**: Comprehensive test coverage with validation
5. **Review**: Scrum Master validates completion against acceptance criteria

### Agent Collaboration Patterns
- **Context-Engineered**: All agents work with comprehensive project context
- **Sequential Execution**: Tasks executed in defined order with checkpoints
- **Quality Gates**: Validation at each stage before progression
- **Documentation-Driven**: All decisions and changes documented

## GateGrind V2 Requirements & Features

### Functional Requirements
#### V2 Game Systems (New Implementation)
- **Awakening System**: Character awakening mechanics with progression tracking
- **Dungeons System**: Dungeon exploration with rewards and challenges
- **Skill Tree System**: Comprehensive skill progression and unlocking
- **Aura System**: Character aura mechanics and visual effects

#### V1 Features (Re-implementation)
- **Movement Logging**: Enhanced movement tracking and validation
- **XP Engine**: Experience point calculation and progression
- **Incursions System**: Raid-like events and participation tracking
- **Daily Login Rewards**: Reward system for consistent engagement

#### Core Platform Features
- **V2 Movement Library**: New movement tracking and validation system
- **Dual-Path Progression**: Support for both V1 and V2 progression systems
- **API-First Design**: All game mechanics accessible via REST API
- **Discord Integration**: Seamless bot integration with game systems

### Non-Functional Requirements
#### Performance & Scalability
- **Asynchronous Operations**: All database and external API calls use async/await
- **Connection Pooling**: Optimized database connection management
- **Caching Strategy**: Redis caching for frequently accessed data
- **Response Times**: API endpoints respond within 200ms for standard operations

#### Quality & Reliability
- **Test Coverage**: Minimum 80% code coverage across all modules
- **Error Handling**: Comprehensive exception handling with Sentry monitoring
- **Data Validation**: Pydantic schemas for all API requests/responses
- **Database Integrity**: Foreign key constraints and data validation

#### User Experience
- **UI/UX Consistency**: Consistent design patterns across Discord and web interfaces
- **API Documentation**: Auto-generated OpenAPI documentation
- **Error Messages**: Clear, actionable error messages for users
- **Performance Feedback**: Real-time feedback for user actions

#### Observability & Monitoring
- **Sentry Integration**: Error tracking and performance monitoring
- **Logging Strategy**: Structured logging with appropriate log levels
- **Health Checks**: API health endpoints for monitoring
- **Metrics Collection**: Key performance indicators tracking
## 🚨 BMad V2 Development Rules

### CRITICAL RULES FOR BMad V2 AGENTS

1. **ALWAYS CHECK SENTRY FIRST** when debugging errors:
   - Organization: `tomi-sakkos`
   - Region URL: `https://de.sentry.io`
   - Check recent exceptions before other debugging approaches

2. **V2 COMPONENT LOCATIONS** - Use correct paths:
   - **Models**: `/app/infrastructure/database/models/v2/`
   - **Schemas**: `/app/api/v2/schemas/`
   - **Services**: `/app/application/services/`
   - **API Endpoints**: `/app/api/v2/`

3. **FOLLOW V2 PATTERNS**:
   - Inherit from `BaseService` for all business logic
   - Use dependency injection for service access
   - Follow XP Engine patterns for progression
   - Implement comprehensive async testing (93% coverage minimum)

4. **SCHEMA REFERENCES**: Use correct import paths:
   ```python
   from app.api.v2.schemas.movement_schemas import MovementCategoryResponse
   from app.api.v2.schemas.movement_logging_schemas import LogMovementRequest
   ```

5. **DATABASE OPERATIONS**:
   - Use V2 models from `/app/infrastructure/database/models/v2/`
   - Follow Alembic migration patterns
   - Ensure idempotent seeding scripts

### Development Guidelines
- **New API Endpoints**: Create in `/app/api/v2/`
- **New Models**: Create in `/app/infrastructure/database/models/v2/`
- **New Services**: Create in `/app/application/services/`
- **New Tests**: Follow existing patterns in `/tests/`
- **Schema References**: Use V2 schemas from `/app/api/v2/schemas/`

### Import Patterns to Follow
```python
# V2 Models (CORRECT)
from app.infrastructure.database.models.v2.ascendants import Ascendant

# V2 Schemas (CORRECT)
from app.api.v2.schemas.movement_schemas import MovementCategoryResponse

# V2 Services (CORRECT)
from app.application.services.movement_service import MovementService

# V2 API (CORRECT)
from app.api.v2.movements import router
```

### Import Patterns to AVOID
```python
# V1 Models (AVOID for new development)
from core.database.models.user import User

# V1 Routes (AVOID for new development)  
from api.routes.users import router

# V1 Features (AVOID for new development)
from features.user.logic.user_service import UserService
```

## Common Development Tasks

### Adding New V2 API Endpoint
1. Create route in `/app/api/v2/`
2. Use existing schemas from `/api/schemas/v2/`
3. Create service in `/app/application/services/`
4. Add tests in `/tests/`

### Adding New V2 Model
1. Create model in `/app/infrastructure/database/models/v2/`
2. Create migration with Alembic
3. Update repository in `/app/infrastructure/repositories/`
4. Add tests in `/tests/`

### Working with Existing V1 Features
1. **Understand**: V1 features are in `/features/` and `/core/`
2. **Extend**: Add V2 API endpoints that interface with V1 logic
3. **Migrate**: Gradually move V1 logic to V2 services when needed

## Key Files & Entry Points

### Main Application Files
- **V1 Legacy**: `main_v1.py` - Discord bot + FastAPI hybrid (legacy)
- **V2 Current**: `app/main.py` - Clean FastAPI-only API server (preferred)
- **Configuration**: `core/config.py` - Application configuration and environment variables
- **Database**: `core/database/db.py` - Database connection and session management

### V2 Implementation Files
- **V2 Models**: `app/infrastructure/database/models/v2/` - All V2 SQLAlchemy models
- **V2 Schemas**: `app/api/v2/schemas/` - Pydantic request/response models
- **V2 Services**: `app/application/services/` - Business logic layer
- **V2 Endpoints**: `app/api/v2/` - FastAPI routers and endpoints
- **V2 Migration**: `alembic/versions/f635a66fc269_initial_v2_schema_migration.py`

### Architecture Documentation
- `docs/architecture/overview.md` - High-level architecture overview
- `docs/architecture/technology-stack.md` - Detailed technology stack
- `docs/architecture/project-structure.md` - Directory structure guide
- `docs/core-architecture.md` - BMad Method framework details
- `docs/greenfield-architecture.md` - GateGrind V2 technical architecture

### Configuration & Dependencies
- `.bmad-core/core-config.yaml` - BMad V2 agent configuration
- `pyproject.toml` - Python dependencies and project metadata
- `requirements.txt` - Python package dependencies
- `alembic.ini` - Database migration configuration
- `pytest.ini` - Test configuration

### Testing & Quality
- `tests/conftest.py` - Test configuration and shared fixtures
- `tests/README.md` - Comprehensive testing documentation
- `flattened-codebase.xml` - Complete codebase reference for agents

### Story Documentation (Completed V2 Features)

#### Epic 1: Foundation
- `docs/stories/1.1.v2-database-schema.md` - V2 database models and schema design
- `docs/stories/1.2.v2-service-layer.md` - Service layer architecture and patterns
- `docs/stories/1.3.foundational-service-layer-core-api.md` - Core API foundation

#### Epic 2: Core Mechanics
- `docs/stories/2.1.re-implement-user-registration.md` - User registration V2 implementation
- `docs/stories/2.2.re-implement-movement-reps-logging.md` - Movement logging and XP calculation

#### Epic 3: Progression & Skill Tree
- `docs/stories/3.1.skill-tree-system.md` - Skill tree implementation and progression
- `docs/stories/3.2.milestone-progression.md` - Milestone and stat progression system

#### Epic 4: Aura Power Level System
- `docs/stories/4.1.implement-aura-calculation.md` - Aura score calculation using formula: (Level * 100) + (STR*10 + END*10 + TECH*5) + (Nodes Unlocked * 25)
- `docs/stories/4.2.real-time-aura-updates.md` - Real-time Aura updates across all API endpoints with AuraUpdateInfo model

#### Epic 5: Awakening & Dungeon Systems
- `docs/stories/5.1.awakening-system.md` - Daily Awakening challenge system with personalized quests, Shadow Keys rewards, and streak tracking

## Context Usage for BMad V2 Agents

### Primary Use Cases
1. **Project Understanding**: Comprehensive context for new agents joining the project
2. **Development Decisions**: Informed choices that align with existing architecture
3. **Code Consistency**: Maintain established patterns and conventions
4. **Integration Guidance**: Proper integration with Discord bot and API systems
5. **Testing Standards**: Follow established testing and quality patterns

### Agent Workflow Integration
- **Story Execution**: Use this context alongside story requirements
- **Architecture Alignment**: Ensure all changes align with V2 migration strategy
- **Quality Assurance**: Follow testing standards and coverage requirements
- **Documentation Updates**: Keep documentation current with code changes

### Critical Success Factors
- **Context-Driven Development**: All decisions based on comprehensive project understanding
- **Migration Awareness**: Respect the V1/V2 mixed architecture during transition
- **Quality First**: Maintain high standards for testing, documentation, and code quality
- **Collaboration**: Work effectively with other BMad agents using shared context

Remember: This is a **working codebase in active V2 migration**. The mixed V1/V2 architecture is intentional and functional. Focus on using V2 patterns for new development while respecting the existing working state and comprehensive testing requirements.