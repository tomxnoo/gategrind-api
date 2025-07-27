# Workspace Handoff: Story 6.1 - Discord Bot V2 API Integration

## Executive Summary

**Project**: RoS-TRAE Discord Bot V2 API Migration  
**Current Branch**: Dungeon-BMAD  
**Backend Status**: 92% Complete (12/13 stories implemented)  
**Primary Task**: Update Discord bot to use V2 API endpoints  
**Critical Issue**: 44 failing tests due to authentication import mismatch  

## 🚨 Critical Fix Required

### Authentication Import Issue
The V2 API uses a different authentication function than V1:
- **V1**: `get_current_user` 
- **V2**: `get_current_user_id` from `app.api.v2.dependencies.auth`

All tests and Discord bot code must be updated to use the new authentication pattern.

## Current System State

### ✅ What's Working
1. **V2 Backend Services** (100% functional at service layer)
   - Movement logging and XP calculation
   - Skill tree progression and unlocking
   - Awakening daily challenges
   - Dungeon system with infinite progression
   - Real-time aura updates

2. **Database Layer** 
   - All V2 models implemented
   - Migrations complete
   - Proper indexing and constraints

3. **Service Tests**
   - 24/24 dungeon service tests passing
   - All core functionality validated

### ❌ What Needs Fixing
1. **API Integration Tests** (44 failures)
   - Incorrect authentication imports
   - Missing route configurations
   - Test client setup issues

2. **Discord Bot Integration** (Not started)
   - No V2 API client implementation
   - Missing async response handlers
   - No loading state UI components

## Implementation Roadmap

### Phase 1: Fix Failing Tests (Day 1)
```python
# Fix in all test files
# OLD (incorrect)
from app.api.v2.dungeons import get_current_user

# NEW (correct)
from app.api.v2.dependencies.auth import get_current_user_id
```

### Phase 2: Create V2 API Client (Days 2-3)
```python
# Location: bot/services/api_client_v2.py
class V2APIClient:
    """Async API client for V2 endpoints"""
    
    def __init__(self, base_url: str, jwt_service: JWTService):
        self.base_url = f"{base_url}/api/v2"
        self.jwt_service = jwt_service
        self.session = aiohttp.ClientSession()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs):
        """Base request method with auth and error handling"""
        token = await self.jwt_service.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        async with self.session.request(
            method, 
            f"{self.base_url}{endpoint}", 
            headers=headers,
            **kwargs
        ) as response:
            data = await response.json()
            if not data.get('success'):
                raise V2APIError(data.get('error'))
            return data
```

### Phase 3: Implement Feature Endpoints (Days 4-7)

#### Movement Logging
```python
async def log_movement(self, user_id: int, movement_data: dict):
    """Log movement activity"""
    return await self._make_request(
        'POST', 
        '/events/log-movement',
        json={'user_id': user_id, **movement_data}
    )
```

#### Dungeon System (Complex Flow)
```python
async def enter_dungeon(self, user_id: int, level: int):
    """Enter dungeon with async trial generation"""
    response = await self._make_request(
        'POST',
        '/dungeons/enter',
        json={'user_id': user_id, 'level': level}
    )
    
    # Handle async loading state
    session_id = response['data']['session_id']
    return DungeonSession(session_id, response['data'])

async def poll_dungeon_status(self, session_id: str):
    """Poll for trial generation completion"""
    return await self._make_request(
        'GET',
        f'/dungeons/session/{session_id}'
    )
```

### Phase 4: Discord UI Integration (Days 8-10)

#### Loading States for Async Operations
```python
# Location: bot/ui/components/loading.py
class DungeonLoadingView(discord.ui.View):
    def __init__(self, session_id: str):
        super().__init__(timeout=30)
        self.session_id = session_id
        self.add_item(LoadingSpinner())
    
    async def poll_and_update(self, interaction: discord.Interaction):
        """Poll API and update UI when ready"""
        while True:
            status = await api_client.poll_dungeon_status(self.session_id)
            if status['data']['trials_ready']:
                dungeon_view = DungeonTrialsView(status['data'])
                await interaction.edit_original_response(
                    embed=dungeon_view.embed,
                    view=dungeon_view
                )
                break
            await asyncio.sleep(2)
```

## V2 Endpoint Reference

### Core Endpoints to Implement

| Feature | V1 Endpoint | V2 Endpoint | Response Format |
|---------|-------------|-------------|-----------------|
| Profile | GET /v1/profile | GET /v2/users/me/profile | StandardV2Response |
| Movement Log | POST /v1/log-movement | POST /v2/events/log-movement | MovementLogResponse |
| Skill Tree | GET /v1/skill-tree | GET /v2/movements/library | SkillTreeResponse |
| Awakening | POST /v1/awakening | POST /v2/awakening/generate | AwakeningResponse |
| Dungeons | N/A (new) | POST /v2/dungeons/enter | DungeonEntryResponse |

### V2 Response Structure
```typescript
interface V2Response<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  aura_update?: {
    previous_aura: number;
    current_aura: number;
    change: number;
    reason: string;
  };
}
```

## Testing Strategy

### Unit Tests
```python
# Location: tests/bot/test_v2_api_client.py
@pytest.mark.asyncio
async def test_dungeon_entry():
    client = V2APIClient("http://test", mock_jwt_service)
    
    with aioresponses() as mocked:
        mocked.post(
            'http://test/api/v2/dungeons/enter',
            payload={'success': True, 'data': {...}}
        )
        
        result = await client.enter_dungeon(1, 5)
        assert result.session_id == "test-session"
```

### Integration Tests
```python
# Location: tests/bot/test_discord_integration.py
@pytest.mark.asyncio
async def test_dungeon_command_flow():
    """Test full dungeon command flow with loading states"""
    bot = create_test_bot()
    ctx = create_mock_context()
    
    # Simulate command
    await bot.dungeon_command(ctx, level=1)
    
    # Verify loading state shown
    assert ctx.responded
    assert "Generating dungeon" in ctx.response.embeds[0].description
    
    # Verify final state after polling
    await asyncio.sleep(3)
    assert "Trial 1:" in ctx.response.embeds[0].description
```

## Common Pitfalls to Avoid

1. **Authentication Headers**
   - Always use `Bearer` prefix for JWT tokens
   - Handle token refresh automatically

2. **Async Response Patterns**
   - Don't block on long operations
   - Implement proper polling with exponential backoff
   - Show loading states immediately

3. **Error Handling**
   - Map V2 error codes to user-friendly messages
   - Handle network timeouts gracefully
   - Implement retry logic for transient failures

4. **Real-time Updates**
   - Always display aura changes from responses
   - Update user stats after every action
   - Handle concurrent operations properly

## Development Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export JWT_SECRET_KEY="dev-secret-key"
export DATABASE_URL="postgresql://..."
export DEVELOPMENT_MODE="true"

# Run backend API
uvicorn app.main:app --reload --port 5000

# Run tests
pytest tests/test_dungeon_*.py -v

# Run Discord bot (separate terminal)
python bot/main.py
```

## Success Criteria

1. **All V1 endpoints migrated** (100% coverage)
2. **Zero regression** in existing functionality  
3. **All 44 failing tests fixed** and passing
4. **Loading states** implemented for async operations
5. **Real-time aura updates** displayed in UI
6. **Error handling** with user-friendly messages
7. **Performance metrics** meet Discord's 3-second response requirement

## Support Resources

- **Backend API Docs**: `/docs` endpoint when running locally
- **V2 Schema Definitions**: `app/api/v2/schemas/`
- **Service Layer Code**: `app/application/services/`
- **Test Examples**: `tests/test_*.py`

## Contact for Questions

- **Backend Team**: Review service layer implementations
- **Database Team**: Check model relationships
- **QA Team**: Validate test coverage

---

**Ready to Start?** 
1. First, fix the authentication imports to get tests passing
2. Then build the V2 API client with proper async handling
3. Finally, integrate with Discord UI components

Good luck! 🚀