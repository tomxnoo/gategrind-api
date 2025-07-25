# Tests

This directory contains unit tests for the GateGrind V2 application.

## Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_models_v2.py` - Unit tests for V2 database models
- **Awakening System Tests:**
  - `test_awakening_service.py` - Unit tests for awakening service ✅ (12/12 passing)
  - `test_awakening_integration.py` - Integration tests ⚠️ (async fixture issues)
  - `test_awakening_api.py` - API endpoint tests ⚠️ (import issues)

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
- **`test_awakening_service.py` - Complete unit test suite fix (2024-12-19)**

### 🔧 Case Study: Awakening Service Test Fixes (2024-12-19)

**Problem**: All 12 unit tests in `test_awakening_service.py` were failing due to multiple mocking and assertion issues.

**Root Causes Identified:**
1. **Mock Type Mismatches**: Using `AsyncMock` for synchronous methods
2. **Database Transaction Expectations**: Asserting `commit()` when services only call `flush()`
3. **Missing Mock Attributes**: Tests expecting attributes not present on mocks
4. **Parameter Type Errors**: Passing wrong data types to methods
5. **Incorrect Expected Values**: Test expectations not matching actual service logic

**Fixes Applied:**

#### 1. Mock Type Corrections
```python
# ❌ BEFORE - Wrong mock type for synchronous method
service._validate_quest_completion = AsyncMock(return_value=True)

# ✅ AFTER - Correct mock type
service._validate_quest_completion = MagicMock(return_value=True)
```

#### 2. Database Transaction Alignment
```python
# ❌ BEFORE - Wrong transaction expectation
db_session.commit.assert_called()

# ✅ AFTER - Correct expectation matching service implementation
db_session.flush.assert_called()
```

#### 3. Missing Mock Attributes
```python
# ❌ BEFORE - Missing required attribute
mock_progress = MagicMock()

# ✅ AFTER - Complete mock with all required attributes
mock_progress = MagicMock()
mock_progress.awakening_streak = 5
```

#### 4. Parameter Type Fixes
```python
# ❌ BEFORE - Wrong parameter type
result = service._get_quest_count_for_readiness(1)  # Integer

# ✅ AFTER - Correct parameter type
result = service._get_quest_count_for_readiness("low")  # String
```

#### 5. Complex Database Query Mocking
```python
# ✅ Proper mocking for methods using greenlet_spawn and complex queries
@patch('app.application.services.awakening_service.greenlet_spawn')
def test_get_awakening_history(self, mock_greenlet, awakening_service, db_session):
    # Mock the database query result
    mock_session = MagicMock()
    db_session.execute.return_value = mock_session
    
    # Mock greenlet_spawn to return the session directly
    mock_greenlet.return_value = mock_session
    
    # Mock the formatting method
    awakening_service._format_session_for_api = MagicMock(
        return_value={"session_id": 1, "date": "2024-01-01"}
    )
```

**Key Lessons:**
- Always check if methods are synchronous or asynchronous before choosing mock type
- Verify what database operations services actually perform (flush vs commit)
- Ensure all mock objects have the attributes that tests expect
- Match parameter types exactly as defined in service methods
- For complex database operations, mock at the appropriate level (execute, greenlet_spawn, etc.)

**Result**: All 12 unit tests now pass consistently, providing reliable coverage for the awakening service.

### 🚀 Quick Debug Tips

If you see these errors:
- **"coroutine object does not support async context manager"** → Check session.begin() mocking
- **"method object has no attribute return_value"** → You're setting return_value on a real method, use AsyncMock
- **"coroutine was never awaited"** → Missing await or improper async mock setup

**Always check**: Are you using the same mocking pattern as working tests?

## 🔍 Awakening System Test Troubleshooting

### Current Status (2024-12-19)
- ✅ **Unit Tests**: `test_awakening_service.py` - All 12 tests passing
- ⚠️ **Integration Tests**: `test_awakening_integration.py` - Async fixture issues
- ⚠️ **API Tests**: `test_awakening_api.py` - Import issues

### Common Issues & Solutions

#### 1. Mock Type Selection for Awakening Service
```python
# ✅ CORRECT - Synchronous methods use MagicMock
service._validate_quest_completion = MagicMock(return_value=True)
service._format_session_for_api = MagicMock(return_value={})

# ❌ WRONG - Don't use AsyncMock for synchronous methods
service._validate_quest_completion = AsyncMock(return_value=True)  # Fails!
```

#### 2. Database Transaction Expectations
```python
# ✅ CORRECT - Awakening service uses flush(), not commit()
db_session.flush.assert_called()

# ❌ WRONG - Service doesn't call commit()
db_session.commit.assert_called()  # Fails!
```

#### 3. Required Mock Attributes
```python
# ✅ CORRECT - Include all attributes used by service
mock_progress = MagicMock()
mock_progress.awakening_streak = 5  # Required by create_daily_session

# ❌ WRONG - Missing attributes cause AttributeError
mock_progress = MagicMock()  # Missing awakening_streak
```

#### 4. Parameter Types for Quest Methods
```python
# ✅ CORRECT - Use string readiness levels
service._get_quest_count_for_readiness("low")    # Returns 3
service._get_quest_count_for_readiness("high")   # Returns 4
service._get_difficulty_for_readiness("low")     # Returns "easy"

# ❌ WRONG - Don't use integers
service._get_quest_count_for_readiness(1)  # Fails!
```

#### 5. Complex Query Mocking (greenlet_spawn)
```python
# ✅ CORRECT - Mock both execute and greenlet_spawn
@patch('app.application.services.awakening_service.greenlet_spawn')
def test_method(self, mock_greenlet, service, db_session):
    mock_session = MagicMock()
    db_session.execute.return_value = mock_session
    mock_greenlet.return_value = mock_session
```

### Integration Test Issues (TODO)
The integration tests currently fail due to:
- Async fixture setup problems
- Quest generation service interactions
- Database session management in async context

### API Test Issues (TODO)
The API tests currently fail due to:
- Import path issues
- Missing dependencies
- Endpoint configuration problems