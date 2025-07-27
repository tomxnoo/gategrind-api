# Story 6.1: Update Bot API Client

## Status
In Progress

## Story
**As a** developer,
**I want** the Discord bot's API client to be updated to communicate with the new V2 endpoints,
**so that** the bot can leverage all the new V2 backend features and provide users with enhanced functionality.

## Acceptance Criteria

### API Client Migration
- [ ] All V1 API calls in the Discord bot are updated to point to new V2 endpoints
- [ ] Client correctly handles new V2 data schemas and response formats
- [ ] Error handling is updated for V2-specific error codes and messages
- [ ] Authentication flow is compatible with V2 JWT token system

### Response Handling
- [ ] Bot correctly processes the new standardized response format with success/error structure
- [ ] Real-time aura updates from V2 responses are handled and displayed appropriately
- [ ] Async response patterns for dungeon operations are properly implemented
- [ ] New data structures (profile DTOs, skill tree data, quest objects) are parsed correctly

### V2 Feature Integration
- [ ] Profile data fetching uses GET /v2/users/me/profile endpoint
- [ ] Movement logging uses POST /v2/events/log-movement endpoint
- [ ] Skill tree data fetching uses GET /v2/movements/library endpoint
- [ ] Awakening system integration with POST /v2/awakening/generate endpoint
- [ ] Dungeon system integration with POST /v2/dungeons/enter endpoint

### Error Handling & Monitoring
- [ ] V2-specific error codes are mapped to appropriate user-friendly messages
- [ ] Failed API calls are logged with sufficient detail for debugging
- [ ] Fallback mechanisms are in place for API unavailability
- [ ] Rate limiting handling for V2 endpoints is implemented

### Testing & Validation
- [ ] All API client changes are covered by unit tests
- [ ] Integration tests verify end-to-end functionality with V2 backend
- [ ] Performance testing ensures response times meet user experience requirements
- [ ] Error scenarios are tested and handled gracefully

## Dev Notes

### Previous Story Insights
From Story 5.2 (Dungeon System), key learnings include:
- Comprehensive async/await patterns are essential for Discord bot responsiveness
- Proper error handling with custom exceptions improves user experience
- Real-time aura updates must be consistently implemented across all progression events
- Session management requires careful state tracking for long-running operations

### API Specifications
[Source: architecture/api-specification.md#core-endpoints]

**V2 Endpoint Migration Map:**
- Profile: `GET /v1/profile` → `GET /v2/users/me/profile`
- Movement Logging: `POST /v1/log-movement` → `POST /v2/events/log-movement`
- Skill Tree: `GET /v1/skill-tree` → `GET /v2/movements/library`
- Awakening: `POST /v1/awakening` → `POST /v2/awakening/generate`
- Dungeons: `POST /v1/dungeons` → `POST /v2/dungeons/enter`

**New Response Format Structure:**
```json
{
  "success": boolean,
  "data": {
    // Endpoint-specific data
  },
  "aura_update": {
    "previous_aura": number,
    "new_aura": number,
    "change": number,
    "reason": string
  },
  "error": {
    "code": string,
    "message": string,
    "details": object
  }
}
```

**Authentication Requirements:**
[Source: architecture/api-specification.md#authentication--authorization]
- JWT tokens for API authentication
- Discord user ID mapping to internal user IDs
- Rate limiting per-user to prevent abuse

### Data Models
[Source: architecture/api-specification.md#user-profile-management]

**Profile DTO Structure:**
- Ascendant data (id, discord_id, username, level, global_xp, aura, last_login)
- Stats breakdown (strength, endurance, technique with levels, XP, points, milestones)
- Progression data (unlocked_skills, available_points, next_milestone)
- Daily status (awakening_completed, login_reward_claimed, shadow_keys, active_quests)

**Skill Tree Library Structure:**
- Categories with skill nodes
- Node requirements (ascendant_level, stat points)
- Movement data with XP per rep

**Error Response Structure:**
- Standard error codes (INSUFFICIENT_POINTS, etc.)
- Detailed error messages with context
- HTTP status code mapping

### File Locations
[Source: architecture/project-structure.md#directory-structure]

**Discord Bot Integration Points:**
- API client updates likely in bot's service layer
- Response handling in bot's data processing modules
- Error handling in bot's exception management system
- Testing in bot's test suite structure

**Key Integration Files (Bot Side):**
- Bot API client/service classes
- Discord command handlers
- Data transformation utilities
- Error handling middleware

### Testing Requirements
[Source: architecture/project-structure.md#testing-organization]

**Test Coverage Areas:**
- Unit tests for API client methods
- Integration tests for V2 endpoint communication
- Error handling tests for various failure scenarios
- Performance tests for response time requirements
- Mock testing for API unavailability scenarios

**Test Data Requirements:**
- Sample V2 response fixtures
- Error response fixtures
- Authentication token fixtures
- Rate limiting test scenarios

### Technical Constraints
[Source: architecture/technology-stack.md#core-technologies]

**Technology Alignment:**
- Bot must maintain compatibility with FastAPI V2 responses
- JWT authentication integration required
- Redis caching on V2 side requires bot-side cache invalidation awareness
- Pydantic V2 schema compatibility for data validation

**Performance Requirements:**
- Response times must meet Discord's interaction response limits
- Async operations for long-running tasks (dungeons) must provide immediate feedback
- Caching strategy must account for V2 backend TTL settings

### Security Considerations
- JWT token refresh logic must be implemented
- Sensitive data handling must follow V2 security patterns
- Rate limiting compliance to prevent bot abuse
- Input validation alignment with V2 Pydantic schemas

## Implementation Context

### Current Backend Status
- **V2 Backend**: 92% complete (12/13 stories implemented)
- **Authentication**: Uses `get_current_user_id` from `app.api.v2.dependencies.auth`
- **Dungeon System**: Fully implemented with 9 endpoints
- **All V2 Systems**: Operational and tested at service layer

### Critical Import Fix Required
The V2 authentication uses `get_current_user_id` not `get_current_user`. All tests and bot integration must be updated accordingly.

## Tasks / Subtasks

### Task 1: Update Core API Client (AC: 1, 2)
- [ ] Identify all V1 API calls in Discord bot codebase
- [ ] Create mapping document for V1 to V2 endpoint migration
- [ ] Update base API client class to use V2 endpoint URLs
- [ ] Implement new response parsing for V2 standardized format
- [ ] Update authentication flow to use V2 JWT tokens with `get_current_user_id`
- [ ] Implement error handling for V2-specific error codes

### Task 2: Implement V2 Response Handling (AC: 2, 3)
- [ ] Create data models for V2 response structures (Profile DTO, etc.)
- [ ] Implement aura update processing and display logic
- [ ] Add support for async response patterns (dungeon operations)
- [ ] Update existing command handlers to use new response structures
- [ ] Implement response validation using V2 schemas

### Task 3: Migrate Feature-Specific Endpoints (AC: 3)
- [ ] Update profile fetching to use GET /v2/users/me/profile
- [ ] Migrate movement logging to POST /v2/events/log-movement
- [ ] Update skill tree data fetching to GET /v2/movements/library
- [ ] Integrate awakening system with POST /v2/awakening/generate
- [ ] Implement dungeon system integration with full endpoint suite:
  - POST /v2/dungeons/enter - Enter dungeon
  - POST /v2/dungeons/complete-trial - Complete trials
  - GET /v2/dungeons/session/{session_id} - Get session status
  - GET /v2/dungeons/progress/{user_id} - Get user progress
  - GET /v2/dungeons/daily-modifier - Get daily modifier
  - POST /v2/dungeons/recover - Recover sessions
  - POST /v2/dungeons/abandon/{session_id} - Abandon sessions
- [ ] Add task status checking for async operations

### Task 4: Enhanced Error Handling (AC: 4)
- [ ] Create error code mapping for V2-specific errors
- [ ] Implement user-friendly error message translation
- [ ] Add comprehensive logging for failed API calls
- [ ] Implement fallback mechanisms for API unavailability
- [ ] Add rate limiting detection and handling

### Task 5: Testing and Validation (AC: 5)
- [ ] Create unit tests for updated API client methods
- [ ] Implement integration tests with V2 backend
- [ ] Add performance tests for response time validation
- [ ] Create error scenario tests (network failures, invalid responses)
- [ ] Add mock tests for API unavailability scenarios
- [ ] Validate all error paths and edge cases

### Task 6: Documentation and Migration Guide
- [ ] Document all API endpoint changes
- [ ] Create troubleshooting guide for common migration issues
- [ ] Update bot deployment procedures for V2 compatibility
- [ ] Create rollback plan in case of critical issues

## Project Structure Notes

Based on the project structure analysis, the Discord bot integration will need to align with the V2 backend's organized API layer (`app/api/v2/`) and follow the same response patterns. The bot's API client should mirror the service organization found in the backend's application layer for consistency.

## Integration Dependencies

This story depends on:
- All V2 backend systems being fully functional (✅ Complete)
- V2 API endpoints being thoroughly tested (✅ Complete)
- Authentication system being production-ready (✅ Complete)
- Error handling patterns being established (✅ Complete)

## Implementation Details

### API Client Architecture
```python
class V2APIClient:
    """Updated API client for V2 endpoints"""
    
    def __init__(self, base_url: str, jwt_token: str):
        self.base_url = base_url.rstrip('/') + '/api/v2'
        self.headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def enter_dungeon(self, user_id: int, level: int) -> DungeonEntryResponse:
        """Enter a dungeon level"""
        response = await self.session.post(
            f'{self.base_url}/dungeons/enter',
            json={'user_id': user_id, 'level': level}
        )
        return await self._parse_response(response, DungeonEntryResponse)
    
    async def log_movement(self, user_id: int, movement_data: dict) -> MovementLogResponse:
        """Log movement activity"""
        response = await self.session.post(
            f'{self.base_url}/events/log-movement',
            json={'user_id': user_id, **movement_data}
        )
        return await self._parse_response(response, MovementLogResponse)
```

### Discord Bot Integration Pattern
```python
@bot.slash_command(name="dungeon", description="Enter a dungeon")
async def dungeon_command(ctx: discord.ApplicationContext, level: int):
    """Discord command to enter dungeon"""
    # Get user mapping
    user_id = await bot.get_user_id_from_discord(ctx.author.id)
    
    # Call V2 API
    try:
        response = await api_client.enter_dungeon(user_id, level)
        
        # Handle async loading state
        loading_embed = create_loading_embed("Generating dungeon trials...")
        await ctx.respond(embed=loading_embed)
        
        # Update with actual trials when ready
        if response.success:
            dungeon_embed = create_dungeon_embed(response.data)
            await ctx.edit_original_response(embed=dungeon_embed)
        else:
            error_embed = create_error_embed(response.error.message)
            await ctx.edit_original_response(embed=error_embed)
            
    except HTTPException as e:
        await handle_api_error(ctx, e)
```

## Success Metrics

- 100% of V1 API calls successfully migrated to V2
- Zero regression in bot functionality during migration
- Improved response times due to V2 optimizations
- Enhanced user experience with real-time aura updates
- Successful integration with new V2 features (awakening, dungeons)
- All 44 failing API tests resolved with proper authentication

## Risks and Mitigation

**Risk**: Discord bot downtime during migration
**Mitigation**: Implement blue-green deployment strategy with rollback capability

**Risk**: V2 API response changes breaking bot functionality
**Mitigation**: Comprehensive integration testing and response validation

**Risk**: Authentication issues preventing bot operation
**Mitigation**: Thorough JWT token handling testing and fallback mechanisms