# Project Rules & Guidelines

## Version Control
- **Branch Protection**: Main branch requires PR reviews
- **Commit Messages**: Use conventional commits (feat:, fix:, docs:, etc.)
- **PR Requirements**: Include description, testing notes, and link to related issues

## API Development
- **Versioning**: All new endpoints use `/v2/` prefix
- **Response Format**: Consistent JSON structure with proper HTTP status codes
- **Error Handling**: Standardized error responses with meaningful messages
- **Documentation**: OpenAPI/Swagger docs auto-generated from FastAPI

## Engineering Standards
- **Code Quality**: Use Ruff for linting, Black for formatting
- **Testing**: Minimum 80% test coverage for new code
- **Type Hints**: All functions must include proper type annotations
- **Logging**: Structured logging with appropriate levels (DEBUG, INFO, WARN, ERROR)

## File Organization
- **Services**: Business logic in `app/application/services/`
- **Models**: Database models in `app/infrastructure/database/models/v2/`
- **API Routes**: REST endpoints in `app/api/v2/`
- **Tests**: Mirror source structure in `tests/` directory

## Compliance Checklist
Before merging any PR:
- [ ] Code follows established patterns
- [ ] Tests pass with adequate coverage
- [ ] Documentation updated if needed
- [ ] No hardcoded secrets or credentials
- [ ] Error handling implemented
- [ ] Logging added for debugging

---

# GateGrind V2 Development Rules

## Core Principles
- **Clean Architecture**: Follow hexagonal architecture with clear layer separation
- **Domain-Driven Design**: Business logic isolated in domain layer
- **Test-Driven Development**: Write tests before implementation
- **API-First**: Design APIs before building features
- **Single Source of Truth**: The GateGrind V2 - Definitive PRD (greenfield-prd.md) and GateGrind V2 - Final Consolidated Architecture (greenfield-architecture) are the definitive guides
- **Brownfield x Greenfield = V2**: This project is a hybrid. New V2 systems will be built from scratch. Proven V1 features (Movement Logging, XP Engine, Incursions) will be cleanly re-implemented, using the old code as a logical reference but not a direct copy

### 🚨 CRITICAL: V2 File Location Requirement
**All new V2 files MUST be placed within the `/app` folder structure.**

- **Rationale**: Maintain clear separation between V1 legacy code and V2 new development
- **Enforcement**: Any V2 feature, service, configuration, or component must reside in `/app/`
- **V1 Legacy Code**: Remains in current locations for compatibility, only modified for critical bug fixes or V2 integration points

## Architecture

### Hexagonal Architecture Implementation
- **API Layer** (`app/api/v2/`): HTTP request handling and response formatting
  - Controllers for user endpoints, movements, progression, awakening, dungeons, events
  - FastAPI dependencies and middleware
  - Request/response validation using Pydantic
- **Application Layer** (`app/application/`): Business logic orchestration
  - Services: Core business logic implementation
  - Tasks: Background job processing
  - DTOs: Data transfer objects for API responses
- **Domain Layer** (`app/domain/`): Core business entities and rules
  - Entities: Pure business objects with behavior
  - Schemas: Pydantic models for validation and serialization
  - Enums: Domain-specific enumerations and constants
- **Infrastructure Layer** (`app/infrastructure/`): External system integration
  - Database: SQLAlchemy models and session management
  - Repositories: Data access layer with clean interfaces
  - Cache: Redis implementation for performance optimization
  - External: Third-party API clients (Discord, Sentry)

### Current Implementation Status
- **Implemented Services**: ProgressionService, MovementService, IncursionService, MovementLoggingService
- **API Endpoints**: Movements V2, Progression V2, Incursions V2
- **Database Models**: Complete V2 model structure with proper relationships
- **Repository Pattern**: Base repository with specialized implementations

### Dependencies Flow
- **Inward Direction**: Dependencies flow toward domain core
- **Interface Definition**: Domain layer defines contracts, infrastructure implements
- **Dependency Injection**: Services use constructor injection for testability
- **Transaction Management**: Handled at application service layer

## Code Quality
- **Type Safety**: Full type annotations required for all functions and methods
- **Error Handling**: Custom exceptions with proper error codes and meaningful messages
- **Validation**: Pydantic models for all data validation and serialization
- **Documentation**: Comprehensive docstrings for all public methods and classes
- **Service Patterns**: All services inherit from BaseService for consistent patterns

## Observability
- **Primary Observability**: Sentry-based observability stack for production reliability
  - **Error Tracking**: Automatic error reporting to Sentry with full context and stack traces
  - **Performance Monitoring**: Application performance monitoring and bottleneck detection
  - **Release Tracking**: Error tracking across different deployment versions
  - **Custom Context**: Rich error context with user IDs, request IDs, and business logic state
- **Structured Logging**: Python's built-in logging with structured JSON format
  - **Correlation IDs**: Request tracking across service boundaries
  - **Log Levels**: Appropriate use of DEBUG, INFO, WARNING, ERROR levels
  - **Contextual Data**: Include user context, operation context, and timing information
- **Development Debugging**: MCP Logfire tool available in IDE for development-time debugging
  - **Query Capabilities**: Use MCP tools to query logs and traces during development
  - **Local Analysis**: Debug issues locally without requiring external services
- **Health Monitoring**: Built-in health checks and metrics collection
  - **Endpoint Health**: Service availability monitoring
  - **Database Health**: Connection pool and query performance monitoring
  - **Redis Health**: Cache availability and performance metrics

## API & Data Modeling
- **RESTful Design**: Follow REST principles consistently across all endpoints
- **Versioning**: Semantic versioning with backward compatibility (V2 implementation)
- **Pagination**: Cursor-based pagination for large datasets
- **Caching**: Redis caching for frequently accessed data (skill trees, user profiles)
- **Response Optimization**: Profile Panel DTO for minimizing API calls
- **Asynchronous Processing**: Background tasks for long-running operations

## Database Conventions
- **ORM**: SQLAlchemy 2.0+ with async support
- **Migrations**: Alembic for schema changes and version control
- **Naming**: Snake_case for tables and columns, consistent with Python conventions
- **Indexes**: Proper indexing for query performance on frequently accessed fields
- **Relationships**: Clear foreign key relationships with proper cascade rules
- **Models Location**: All V2 models in `app/infrastructure/database/models/v2/`

## Testing Strategy
- **Unit Tests**: Test business logic in isolation with mocked dependencies
- **Integration Tests**: Test API endpoints end-to-end with real database
- **Service Tests**: Test service layer with repository mocks
- **Repository Tests**: Test data access layer with test database
- **Fixtures**: Reusable test data and mocks in `tests/fixtures/`
- **Coverage**: Minimum 80% code coverage for all new code

## Technology Stack (Definitive)
- **Runtime**: Python 3.11+
- **Framework**: FastAPI (latest) for high-performance API development
- **Database**: NeonDB (PostgreSQL 16.x) for primary data storage
- **ORM**: SQLAlchemy 2.0+ for robust data access
- **Data Models**: Pydantic 2.x for validation and serialization
- **Caching**: Redis 7.x for high-performance in-memory cache
- **Testing**: Pytest (latest) for comprehensive testing framework
- **Code Quality**: Ruff & Black for linting and formatting
- **Monitoring**: Sentry for real-time error tracking
- **CI/CD**: GitHub Actions for automated testing and deployment

## Progression System Terminology

### Critical Distinction: Stat Points vs Skill Points
It is critical to distinguish between these two concepts:

- **Stat Points (STR, END, TECH)**: These are the actual stat values that grow through exercise logging (e.g., STR: 150, END: 200, TECH: 100). These represent the user's raw physical capabilities.

- **Skill Points**: These are the currency earned from leveling up and stat milestones that users spend to unlock skill tree nodes. Users receive +1 skill point for each stat type when leveling up (e.g., +1 STR skill point, +1 END skill point, +1 TECH skill point).

### Database Field Naming Conventions
Use clear naming conventions to avoid confusion:
- **Stat values**: `str_stat`, `end_stat`, `tech_stat` (the actual stat levels)
- **Skill points**: `str_points`, `end_points`, `tech_points` (the spendable currency)

### Additional Terminology
- **Ascendant**: The user/player entity with progression tracking
- **Global XP**: Overall experience points for character advancement
- **Aura**: Calculated prestige score based on overall progression
- **Skill Tree**: 5-level progression system per movement category
- **Movement Categories**: Organized skill progressions (PULL_VERTICAL, PUSH_HORIZONTAL, etc.)
- **Milestones**: Achievement thresholds that award skill points (every 150 stat points)

## Game Systems Architecture
- **V2 Greenfield Services**: New services built from scratch (DungeonService, AwakeningService, DailyLoginService)
- **V1 Brownfield Re-implementation**: Clean re-implementation of proven features within V2 structure
- **Quest Generation**: Universal quest engine with configurable parameters
- **Incursion System**: Time-limited events with participant tracking
- **Daily Login Rewards**: Streak tracking and reward distribution

## UI/UX Guidelines
- **Consistency**: Maintain consistent visual language across all interfaces
- **Responsiveness**: Ensure all UI components work across different screen sizes
- **Accessibility**: Follow WCAG guidelines for inclusive design
- **Performance**: Optimize for fast loading and smooth interactions
- **Real-time Feedback**: All progression endpoints must return updated Aura scores
- **Discord Integration**: Optimized for Discord bot interface patterns

### Discord Bot Specific Guidelines
- **Component Reuse**: All new UI panels for V2 features must reuse the existing visual components and patterns from the V1 panels (header, footer, loading UI, etc.)
- **Message Consistency**: 1 ephemeral message is used for all V2 bot responses (the bot edits the existing message)
- **User Experience Preservation**: The look, feel, and asynchronous nature of the existing bot UI must be preserved. The new backend is being built to serve this specific, high-quality user experience
- **Visual Patterns**: Maintain consistent styling, color schemes, and layout patterns established in V1

## Development Workflow
- **Brownfield x Greenfield**: V2 supports full greenfield implementation while enabling clean V1 feature re-implementation
- **Service-First Development**: Implement business logic in services before API endpoints
- **Repository Pattern**: Use repository interfaces for all data access
- **Transaction Boundaries**: Manage transactions at service layer, not repository level
- **Background Processing**: Use async tasks for operations that may take time

---

**Last Updated**: 2024-12-19  
**Version**: 2.1 (Merged)  
**Enforcement**: Mandatory for all V2 development