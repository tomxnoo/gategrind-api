# Tests

This directory contains unit tests for the GateGrind V2 application.

## Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_models_v2.py` - Unit tests for V2 database models

## Running Tests

To run the tests, you'll need to install pytest and coverage:

```bash
pip install pytest pytest-cov
```

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=core --cov-report=html
```

## Test Coverage

The tests aim for 80% coverage as specified in the project requirements. The test suite covers:

- Model creation and validation
- Relationship testing
- Constraint validation
- Foreign key relationships
- Unique constraints
- Data integrity checks

## Fixtures

The `conftest.py` file provides several fixtures:

- `db_engine` - In-memory SQLite database for testing
- `db_session` - Database session for each test
- `sample_*_data` - Sample data for creating model instances