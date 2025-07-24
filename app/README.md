# Foundational Service Layer & Core API

This document describes the implementation of the foundational service layer and core API for the Realm of Shadows fitness RPG backend, specifically focusing on the movement and skill tree functionality.

## Overview

The foundational service layer provides a standardized approach to business logic implementation, database interactions, and API endpoint creation. This implementation includes:

- **Base Service Infrastructure**: A reusable `BaseService` class that provides common patterns for all services
- **Movement Service**: A specialized service for handling movement and skill tree operations
- **Core API V2**: RESTful API endpoints for accessing movement and skill tree data
- **Comprehensive Testing**: Unit and integration tests ensuring reliability and maintainability

## Architecture

### Service Layer Structure

```
app/
├── application/
│   ├── __init__.py
│   └── services/
│       ├── __init__.py
│       ├── base_service.py      # Base service class with common patterns
│       └── movement_service.py  # Movement-specific business logic
└── api/
    ├── __init__.py
    └── v2/
        ├── __init__.py
        ├── movements.py         # Movement API endpoints
        └── router.py           # API router configuration
```

### Key Components

#### BaseService (`app/application/services/base_service.py`)

The `BaseService` class provides:
- **Database Session Management**: Automatic creation and cleanup of async database sessions
- **Transaction Boundaries**: Safe transaction handling with automatic rollback on errors
- **Error Handling**: Standardized error handling and logging
- **Health Checks**: Abstract health check interface for service monitoring
- **URL Normalization**: Automatic database URL normalization for different drivers

#### MovementService (`app/application/services/movement_service.py`)

The `MovementService` class extends `BaseService` and provides:
- **Skill Tree Library**: Complete skill tree structure retrieval
- **Movement Categories**: Category listing and individual category access
- **Data Serialization**: Proper JSON serialization of complex database relationships
- **Performance Optimization**: Efficient database queries with proper joins

#### API V2 Endpoints (`app/api/v2/movements.py`)

The API provides the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/movements/library` | GET | Complete skill tree library |
| `/api/v2/movements/categories` | GET | List all movement categories |
| `/api/v2/movements/categories/{id}` | GET | Specific category with skill tree |
| `/api/v2/movements/health` | GET | Service health check |

## Implementation Details

### Database Integration

The service layer integrates with the existing SQLAlchemy ORM models:
- `MovementCategory`: Movement category definitions
- `SkillTreeNode`: 5-level skill tree structure
- `Movement`: Individual movement progressions

### Response Format

The `/api/v2/movements/library` endpoint returns data in the following format:

```json
{
  "categories": [
    {
      "id": "PULL_VERTICAL",
      "name": "Vertical Pulling",
      "primary_stat": "STR",
      "skill_tree": [
        {
          "id": 1,
          "level": 1,
          "name": "Foundation",
          "description": "Basic vertical pulling movements",
          "requirements": {
            "ascendant_level": 1,
            "str_points": 0,
            "end_points": 0,
            "tech_points": 0
          },
          "movements": [
            {
              "id": 1,
              "name": "Negative Pull-ups",
              "xp_per_rep": 1.5,
              "stat_reward_type": "STR"
            }
          ]
        }
      ]
    }
  ]
}
```

### Error Handling

The implementation includes comprehensive error handling:
- **Service Level**: Database errors are caught and wrapped with meaningful messages
- **API Level**: HTTP status codes and error responses follow REST conventions
- **Cleanup**: Database sessions are always properly closed, even on errors

### Testing

The implementation includes comprehensive test coverage:

#### Unit Tests (`tests/test_movement_service.py`)
- Service method testing with mocked dependencies
- Error handling scenarios
- Database session lifecycle
- Data serialization validation

#### Integration Tests (`tests/test_movements_api.py`)
- Complete request/response cycle testing
- API endpoint validation
- Error response testing
- Performance and concurrency testing

## Usage Examples

### Using the Service Layer

```python
from app.application.services.movement_service import MovementService

# Create service instance
service = MovementService()

try:
    # Get complete skill tree library
    library = await service.get_skill_tree_library()
    
    # Get specific category
    category = await service.get_movement_category("PULL_VERTICAL")
    
    # Get all categories
    categories = await service.get_movement_categories()
    
finally:
    # Always clean up
    await service.close_session()
```

### API Usage

```bash
# Get complete skill tree library
curl http://localhost:5000/api/v2/movements/library

# Get all categories
curl http://localhost:5000/api/v2/movements/categories

# Get specific category
curl http://localhost:5000/api/v2/movements/categories/PULL_VERTICAL

# Health check
curl http://localhost:5000/api/v2/movements/health
```

## Configuration

### Environment Variables

The service layer uses the following environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `DEVELOPMENT_MODE`: Set to "true" to skip database connections for development

### Database Requirements

The service requires the following database tables:
- `movement_categories`: Movement category definitions
- `skill_tree_nodes`: Skill tree node structure
- `movements`: Individual movement data

## Performance Considerations

### Database Optimization
- Uses async SQLAlchemy for non-blocking database operations
- Implements proper joins to minimize database queries
- Includes connection pooling for production environments

### Caching Strategy
- Service layer is designed to work with Redis caching (future enhancement)
- Database sessions are reused within service instances
- Proper cleanup prevents connection leaks

### Scalability
- Async/await pattern supports high concurrency
- Service instances are lightweight and can be created per request
- Database connection pooling handles multiple concurrent requests

## Future Enhancements

### Planned Features
1. **Caching Layer**: Redis integration for frequently accessed data
2. **Authentication**: User-specific skill tree progress
3. **Real-time Updates**: WebSocket support for live skill tree updates
4. **Analytics**: Movement usage and progression tracking
5. **Validation**: Input validation and sanitization improvements

### Extension Points
- Additional service classes can extend `BaseService`
- New API versions can be added under `app/api/v3/`
- Service layer can be extended with middleware for cross-cutting concerns

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify `DATABASE_URL` environment variable
   - Check database server availability
   - Ensure proper database permissions

2. **Import Errors**
   - Verify Python path includes project root
   - Check for circular imports
   - Ensure all dependencies are installed

3. **Test Failures**
   - Run tests with proper test database
   - Check for missing test fixtures
   - Verify mock configurations

### Debugging

Enable debug logging by setting the log level:
```python
import logging
logging.getLogger('app.application.services').setLevel(logging.DEBUG)
```

## Contributing

When extending the service layer:
1. Follow the established patterns in `BaseService`
2. Include comprehensive tests for new functionality
3. Update API documentation for new endpoints
4. Ensure proper error handling and cleanup
5. Add performance tests for data-intensive operations

## Dependencies

### Core Dependencies
- `fastapi`: Web framework for API endpoints
- `sqlalchemy`: ORM for database operations
- `asyncpg`: Async PostgreSQL driver
- `pydantic`: Data validation and serialization

### Development Dependencies
- `pytest`: Testing framework
- `pytest-asyncio`: Async test support
- `unittest.mock`: Mocking for unit tests

## License

This implementation is part of the Realm of Shadows fitness RPG backend and follows the project's licensing terms.