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

## 🚨 CRITICAL: Async Service Mocking Guidelines

**READ THIS BEFORE WRITING NEW TESTS** - Following these patterns will save hours of debugging.

### The Problem We Keep Hitting

When testing services that use `execute_in_transaction` and async database operations, improper mocking leads to:
- `TypeError: 'coroutine' object does not support the asynchronous context manager protocol`
- `RuntimeWarning: coroutine was never awaited`
- `AttributeError: 'method' object has no attribute 'return_value'`

### ✅ CORRECT Mocking Patterns

#### 1. Mock Database Session (Already Handled in Fixtures)
```python
@pytest.fixture
def mock_session(self):
    """Create a mock database session."""
    session = AsyncMock()
    # Create a proper async context manager for begin()
    async_context_manager = AsyncMock()
    async_context_manager.__aenter__ = AsyncMock(return_value=session)
    async_context_manager.__aexit__ = AsyncMock(return_value=None)
    session.begin.return_value = async_context_manager
    return session
```

#### 2. Mock Services with Dependencies - Use Complete AsyncMock
```python
# ✅ CORRECT - Use complete AsyncMock for dependent services
@pytest.fixture
def movement_service(self, mock_session):
    service = MovementLoggingService(mock_session)
    
    # Mock progression_service as complete AsyncMock
    service._progression_service = AsyncMock()
    service._progression_service.add_xp = AsyncMock()
    service._progression_service.add_stat_rewards = AsyncMock()
    
    # Mock execute_in_transaction to use mock_session
    async def mock_transaction(func):
        return await func(mock_session)
    service.execute_in_transaction = AsyncMock(side_effect=mock_transaction)
    
    return service
```

#### 3. Setting Return Values on Mocked Services
```python
# ✅ CORRECT - Reference the mocked service correctly
def test_example(self, movement_service, mock_session):
    # Use _progression_service (the AsyncMock) not progression_service
    movement_service._progression_service.add_xp.return_value = progression_result
    movement_service._progression_service.add_stat_rewards.return_value = ProgressionResult()
```

### ❌ COMMON MISTAKES TO AVOID

#### 1. DON'T Mix Real Services with Partial Mocking
```python
# ❌ WRONG - Creates real service then tries to mock methods
service._progression_service = ProgressionService(mock_session)
service._progression_service.add_xp = AsyncMock()  # This fails!
```

#### 2. DON'T Use Wrong Service Reference
```python
# ❌ WRONG - Using progression_service instead of _progression_service
movement_service.progression_service.add_xp.return_value = result
```

#### 3. DON'T Forget to Mock execute_in_transaction
```python
# ❌ WRONG - Missing execute_in_transaction mock
service._progression_service = AsyncMock()
# This will fail when the service calls execute_in_transaction
```

### 📋 Mocking Checklist for New Tests

Before writing a test that involves services with dependencies:

1. **✅ Check existing working tests** - Look at `test_movement_logging_service.py` for patterns
2. **✅ Use complete AsyncMock()** for dependent services, not real instances
3. **✅ Mock execute_in_transaction** to use your mock_session
4. **✅ Reference mocked services correctly** (usually `_service_name`)
5. **✅ Set return_value on AsyncMock objects**, not real methods

### 🔍 Reference Examples

**Working Test Files to Copy Patterns From:**
- `test_movement_logging_service.py` - Correct movement service mocking
- `test_progression_service.py` - Correct progression service mocking
- `test_aura_performance.py` - Fixed performance test mocking

**Recently Fixed Issues:**
- `test_aura_performance.py` - Fixed progression_service mocking (2024-12-19)

### 🚀 Quick Debug Tips

If you see these errors:
- **"coroutine object does not support async context manager"** → Check session.begin() mocking
- **"method object has no attribute return_value"** → You're setting return_value on a real method, use AsyncMock
- **"coroutine was never awaited"** → Missing await or improper async mock setup

**Always check**: Are you using the same mocking pattern as working tests?