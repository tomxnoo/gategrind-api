# Incursions System - Implementation Documentation

## Overview

The Incursions System is a dynamic, community-driven challenge system for the Rise of Strength fitness application. It provides time-limited, collaborative fitness challenges that encourage user engagement and community participation.

## 🎯 Key Features

### Core Functionality
- **Multiple Incursion Types**: SURGE, CHALLENGE, and ANOMALY incursions with different characteristics
- **Flexible Reward System**: XP, BUFF, and ITEM rewards with customizable values
- **Real-time Progress Tracking**: Live updates of community progress toward incursion goals
- **Participant Management**: Track individual contributions and participation history

### Advanced Features
- **Automatic Scheduling**: Intelligent spawn system with configurable cooldowns
- **Spawn Cooldowns**: Global and type-specific cooldowns to prevent spam
- **Weighted Templates**: Configurable spawn rates for different incursion types
- **Health Monitoring**: Comprehensive system health checks and statistics
- **Repository Pattern**: Clean separation of data access and business logic

## 🏗️ Architecture

### Service Layer
```
app/application/services/
├── incursion_service.py      # Core business logic
├── incursion_scheduler.py    # Automatic scheduling with cooldowns
└── base_service.py          # Base service with common functionality
```

### Data Layer
```
app/infrastructure/
├── database/models/v2/
│   └── incursions.py        # Database models
└── repositories/
    └── incursion_repository.py  # Data access layer
```

### API Layer
```
app/api/v2/
└── incursions.py            # REST API endpoints
```

## 📊 Database Schema

### Incursion Model
```python
class Incursion(BaseModel):
    incursion_id: str           # Unique identifier
    title: str                  # Display name
    description: str            # Detailed description
    incursion_type: IncursionType  # SURGE, CHALLENGE, ANOMALY
    target_exercise: str        # Exercise type
    target_reps: int           # Goal repetitions
    current_reps: int          # Current progress
    reward_type: RewardType    # XP, BUFF, ITEM
    reward_value: int          # Reward amount
    reward_description: str    # Reward details
    is_active: bool           # Active status
    status: IncursionStatus   # ACTIVE, COMPLETED, EXPIRED
    expires_at: datetime      # Expiration time
```

### Participant Model
```python
class IncursionParticipant(BaseModel):
    incursion_id: int         # Foreign key to incursion
    user_id: int             # User identifier
    reps_contributed: int    # User's contribution
    participated_at: datetime # Participation timestamp
```

## 🔧 Configuration

### Spawn Cooldown Configuration
```python
class SpawnCooldownConfig:
    min_cooldown_minutes: int = 30      # Minimum global cooldown
    max_cooldown_minutes: int = 120     # Maximum global cooldown
    max_concurrent_incursions: int = 3  # Max active incursions
    type_specific_cooldowns: Dict[IncursionType, int] = {
        IncursionType.SURGE: 45,        # SURGE cooldown (minutes)
        IncursionType.CHALLENGE: 90,    # CHALLENGE cooldown (minutes)
        IncursionType.ANOMALY: 180      # ANOMALY cooldown (minutes)
    }
```

### Incursion Templates
Templates define the characteristics of spawned incursions:
```python
class IncursionTemplate:
    title: str                    # Template name
    description: str              # Template description
    incursion_type: IncursionType # Type of incursion
    target_exercise: str          # Exercise type
    target_reps_range: Tuple[int, int]  # Min/max reps
    reward_type: RewardType       # Reward type
    reward_value_range: Tuple[int, int]  # Min/max reward
    reward_description: str       # Reward description
    duration_hours: float         # Duration in hours
    weight: float                # Spawn probability weight
```

## 🚀 API Endpoints

### Core Endpoints
- `GET /api/v2/incursions/` - List active incursions
- `GET /api/v2/incursions/{id}` - Get specific incursion
- `POST /api/v2/incursions/` - Create new incursion
- `POST /api/v2/incursions/{id}/contribute` - Add participant contribution
- `DELETE /api/v2/incursions/{id}` - End incursion manually

### Management Endpoints
- `GET /api/v2/incursions/stats/overview` - System statistics
- `GET /api/v2/incursions/scheduler/status` - Scheduler status
- `POST /api/v2/incursions/scheduler/start` - Start scheduler
- `POST /api/v2/incursions/scheduler/stop` - Stop scheduler
- `POST /api/v2/incursions/scheduler/force-spawn` - Force spawn incursion

### Health Check
- `GET /api/v2/incursions/health` - System health check

## 💡 Usage Examples

### Creating an Incursion
```python
from app.application.services import IncursionService
from app.infrastructure.database.models.v2.incursions import IncursionType, RewardType

service = IncursionService(session)

incursion = await service.create_incursion(
    title="Morning Push-Up Surge",
    description="Start your day strong!",
    incursion_type=IncursionType.SURGE,
    target_exercise="push_ups",
    target_reps=500,
    reward_type=RewardType.XP,
    reward_value=150,
    reward_description="Morning Warrior XP"
)
```

### Adding Participant Contribution
```python
success = await service.add_participant_contribution(
    incursion_id="surge_123",
    user_id=456,
    reps=25
)
```

### Starting the Scheduler
```python
from app.application.services import IncursionScheduler, SpawnCooldownConfig

config = SpawnCooldownConfig(
    min_cooldown_minutes=30,
    max_cooldown_minutes=120,
    max_concurrent_incursions=3
)

scheduler = IncursionScheduler(service, config)
await scheduler.start()
```

## 🧪 Testing

### Running Tests
```bash
# Run all incursion tests
pytest tests/test_incursions_system.py -v

# Run specific test categories
pytest tests/test_incursions_system.py::TestIncursionModels -v
pytest tests/test_incursions_system.py::TestIncursionService -v
pytest tests/test_incursions_system.py::TestIncursionScheduler -v
```

### Test Coverage
The test suite covers:
- ✅ Database model validation and relationships
- ✅ Service layer business logic
- ✅ Scheduler with spawn cooldowns
- ✅ Repository data access patterns
- ✅ API endpoint functionality
- ✅ Error handling and edge cases
- ✅ Progress tracking and completion detection

### Demo Script
```bash
# Run the interactive demo
python demo_incursions_system.py
```

## 🔄 Spawn Cooldown System

### How It Works
1. **Global Cooldown**: Prevents any incursion from spawning too frequently
2. **Type-Specific Cooldowns**: Each incursion type has its own cooldown timer
3. **Concurrent Limits**: Maximum number of active incursions at once
4. **Weighted Selection**: Templates have different spawn probabilities

### Cooldown Logic
```python
# Check if enough time has passed since last spawn
if last_spawn_time and (current_time - last_spawn_time) < min_cooldown:
    return False

# Check if we're at the concurrent limit
if len(active_incursions) >= max_concurrent_incursions:
    return False

# Check type-specific cooldowns
for incursion_type, last_spawn in last_spawn_by_type.items():
    type_cooldown = type_specific_cooldowns[incursion_type]
    if (current_time - last_spawn) < timedelta(minutes=type_cooldown):
        # Filter out this type from available templates
        continue
```

### Monitoring Cooldowns
```python
status = scheduler.get_cooldown_status()
# Returns:
# {
#     "is_running": bool,
#     "last_spawn_time": datetime,
#     "global_cooldown_remaining": int,  # seconds
#     "type_cooldowns": {
#         "SURGE": {"last_spawn": datetime, "cooldown_remaining": int},
#         "CHALLENGE": {"last_spawn": datetime, "cooldown_remaining": int},
#         "ANOMALY": {"last_spawn": datetime, "cooldown_remaining": int}
#     },
#     "config": SpawnCooldownConfig
# }
```

## 🎮 Incursion Types

### SURGE Incursions
- **Purpose**: Quick, accessible challenges for all users
- **Characteristics**: Lower target reps, shorter duration, frequent spawns
- **Rewards**: Moderate XP rewards
- **Example**: "Morning Push-Up Surge" - 500 push-ups in 3 hours

### CHALLENGE Incursions
- **Purpose**: Difficult challenges for dedicated users
- **Characteristics**: Higher target reps, longer duration, moderate spawns
- **Rewards**: Powerful buffs and high XP
- **Example**: "Elite Squat Challenge" - 2000 squats in 8 hours

### ANOMALY Incursions
- **Purpose**: Rare, special events with unique rewards
- **Characteristics**: Variable difficulty, short duration, very rare spawns
- **Rewards**: Unique items and special buffs
- **Example**: "Temporal Fitness Rift" - 300 burpees in 1 hour

## 📈 Monitoring and Analytics

### System Statistics
```python
stats = await service.get_incursion_stats()
# Returns:
# {
#     "total_incursions": int,
#     "active_incursions": int,
#     "completed_incursions": int,
#     "expired_incursions": int,
#     "total_participants": int,
#     "total_reps_contributed": int,
#     "average_completion_rate": float
# }
```

### Health Monitoring
```python
health = await service.health_check()
# Returns:
# {
#     "status": "healthy" | "degraded" | "unhealthy",
#     "active_incursions": int,
#     "database_connection": bool,
#     "last_cleanup": datetime,
#     "scheduler_running": bool
# }
```

## 🔧 Configuration Options

### Environment Variables
```bash
# Database configuration
DATABASE_URL=postgresql://user:pass@localhost/ros_db

# Incursion system settings
INCURSION_MIN_COOLDOWN_MINUTES=30
INCURSION_MAX_COOLDOWN_MINUTES=120
INCURSION_MAX_CONCURRENT=3
INCURSION_CLEANUP_INTERVAL_MINUTES=15

# Scheduler settings
INCURSION_SCHEDULER_ENABLED=true
INCURSION_AUTO_START_SCHEDULER=true
```

### Customizing Templates
```python
# Add custom incursion templates
custom_template = IncursionTemplate(
    title="Custom Challenge",
    description="Your custom incursion",
    incursion_type=IncursionType.CHALLENGE,
    target_exercise="custom_exercise",
    target_reps_range=(100, 500),
    reward_type=RewardType.XP,
    reward_value_range=(200, 800),
    reward_description="Custom Reward",
    duration_hours=4.0,
    weight=1.0
)

scheduler.incursion_templates.append(custom_template)
```

## 🚨 Error Handling

### Service Layer Errors
- **ValidationError**: Invalid input parameters
- **IncursionNotFoundError**: Incursion doesn't exist
- **IncursionInactiveError**: Trying to contribute to inactive incursion
- **DatabaseError**: Database connection or query issues

### API Error Responses
```json
{
    "error": "IncursionNotFound",
    "message": "Incursion with ID 'invalid_id' not found",
    "status_code": 404
}
```

### Scheduler Error Handling
- Automatic retry on temporary failures
- Graceful degradation when database is unavailable
- Comprehensive logging for debugging

## 🔮 Future Enhancements

### Planned Features
- **User Leaderboards**: Track top contributors across incursions
- **Achievement System**: Unlock achievements for participation
- **Incursion Chains**: Sequential incursions that unlock each other
- **Dynamic Difficulty**: Adjust targets based on community performance
- **Social Features**: Team-based incursions and competitions

### Scalability Considerations
- **Caching Layer**: Redis for frequently accessed data
- **Event Streaming**: Real-time updates via WebSocket
- **Horizontal Scaling**: Support for multiple scheduler instances
- **Analytics Pipeline**: Detailed metrics and user behavior tracking

## 📝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up database: `alembic upgrade head`
4. Run tests: `pytest tests/test_incursions_system.py`
5. Start demo: `python demo_incursions_system.py`

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings for public methods
- Write tests for new features

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Submit pull request with description

## 📄 License

This incursions system is part of the Rise of Strength application and follows the project's licensing terms.

---

**Built with ❤️ for the Rise of Strength community**