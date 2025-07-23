# Core Services Design

## Overview

The GateGrind V2 backend implements a service-oriented architecture within the Application Layer. Services orchestrate business operations, coordinate domain entities, and manage interactions with infrastructure components.

## Service Architecture Principles

### 1. Single Responsibility
Each service has a focused, well-defined purpose and manages a specific domain area.

### 2. Dependency Injection
Services depend on abstractions (interfaces) rather than concrete implementations, enabling testability and flexibility.

### 3. Transaction Management
Services manage transaction boundaries and ensure data consistency across operations.

### 4. Error Handling
Services implement comprehensive error handling and integrate with monitoring systems.

## Core Services

### ProgressionService

**Purpose**: Central hub for all user progression and advancement logic.

**Responsibilities**:
- XP management and distribution
- Level progression calculations
- Stat milestone tracking and rewards
- Skill node unlocking
- Aura calculation and updates

**Key Methods**:

```python
class ProgressionService:
    def __init__(self, 
                 user_repo: UserRepository,
                 skill_repo: SkillRepository,
                 cache_service: CacheService):
        self.user_repo = user_repo
        self.skill_repo = skill_repo
        self.cache_service = cache_service
    
    async def add_xp(self, user_id: int, amount: int, category: str) -> ProgressionResult:
        """
        Adds XP, checks for level-ups, and triggers milestone rewards.
        
        Args:
            user_id: Target user identifier
            amount: XP amount to add
            category: XP category ('global', 'strength', 'endurance', 'technique')
        
        Returns:
            ProgressionResult with level changes, rewards, and updated Aura
        """
        
    async def unlock_skill_node(self, user_id: int, node_id: int) -> UnlockResult:
        """
        Verifies requirements, consumes points, and unlocks skill node.
        
        Args:
            user_id: Target user identifier
            node_id: Skill tree node to unlock
        
        Returns:
            UnlockResult with success status and updated progression
        """
        
    async def calculate_and_update_aura(self, user_id: int) -> int:
        """
        Calculates and updates user's Aura score.
        
        Triggered internally whenever contributing factors change:
        - Level increases
        - Stat improvements
        - Skill unlocks
        - Achievement completions
        
        Args:
            user_id: Target user identifier
        
        Returns:
            New Aura score
        """
```

**Aura Calculation Logic**:
```python
def calculate_aura(self, user_profile: UserProfile) -> int:
    """
    Aura = Base Level Multiplier + Stat Bonuses + Skill Bonuses + Achievement Bonuses
    """
    base_aura = user_profile.level * 10
    
    stat_bonus = (
        user_profile.stats.str_level * 5 +
        user_profile.stats.end_level * 5 +
        user_profile.stats.tech_level * 5
    )
    
    skill_bonus = len(user_profile.unlocked_skills) * 15
    
    # Additional bonuses for rare achievements, dungeon completions, etc.
    achievement_bonus = self._calculate_achievement_bonus(user_profile)
    
    return base_aura + stat_bonus + skill_bonus + achievement_bonus
```

### QuestGenerationService

**Purpose**: Universal quest engine for all quest types and sources.

**Responsibilities**:
- Dynamic quest generation based on user profile
- Quest difficulty scaling
- Reward calculation
- Quest template management

**Key Methods**:

```python
class QuestGenerationService:
    def __init__(self,
                 quest_repo: QuestRepository,
                 movement_repo: MovementRepository,
                 user_service: UserService):
        self.quest_repo = quest_repo
        self.movement_repo = movement_repo
        self.user_service = user_service
    
    async def generate_quests(self, user_id: int, config: QuestConfig) -> List[Quest]:
        """
        Universal quest generation method.
        
        Args:
            user_id: Target user identifier
            config: Quest configuration specifying source, difficulty, focus, etc.
        
        Returns:
            List of generated quests
        """
        
    async def generate_awakening_quests(self, user_id: int) -> List[Quest]:
        """
        Generates daily Awakening quests based on user progression.
        """
        
    async def generate_dungeon_trial(self, user_id: int, dungeon_level: int) -> Quest:
        """
        Generates dungeon trial quest based on level and user capabilities.
        """
```

**Quest Configuration**:
```python
@dataclass
class QuestConfig:
    source: str  # 'Awakening', 'Dungeon', 'Incursion'
    difficulty: str  # 'easy', 'medium', 'hard', 'extreme'
    focus: Optional[str] = None  # 'PUSH_VERTICAL', 'PULL_HORIZONTAL', etc.
    dungeon_level: Optional[int] = None
    daily_modifiers: Optional[Dict] = None
    user_preferences: Optional[Dict] = None
```

### DungeonService

**Purpose**: Manages dungeon entry, progression, and completion logic.

**Responsibilities**:
- Shadow Key management
- Dungeon entry validation
- Trial generation coordination
- Progress tracking
- Reward distribution

**Key Methods**:

```python
class DungeonService:
    def __init__(self,
                 dungeon_repo: DungeonRepository,
                 quest_service: QuestGenerationService,
                 progression_service: ProgressionService):
        self.dungeon_repo = dungeon_repo
        self.quest_service = quest_service
        self.progression_service = progression_service
    
    async def enter_dungeon(self, user_id: int, dungeon_level: int) -> DungeonEntry:
        """
        Validates requirements and initiates dungeon entry.
        
        Process:
        1. Verify Shadow Key availability
        2. Check level/stat requirements
        3. Consume Shadow Key
        4. Generate trial quest
        5. Return asynchronous response
        """
        
    async def complete_dungeon(self, user_id: int, quest_id: int) -> DungeonCompletion:
        """
        Processes dungeon completion and distributes rewards.
        """
```

### AwakeningService

**Purpose**: Manages daily Awakening ritual and quest generation.

**Responsibilities**:
- Daily ritual tracking
- Awakening quest generation
- Shadow Key rewards
- Daily reset logic

**Key Methods**:

```python
class AwakeningService:
    def __init__(self,
                 awakening_repo: AwakeningRepository,
                 quest_service: QuestGenerationService,
                 reward_service: RewardService):
        self.awakening_repo = awakening_repo
        self.quest_service = quest_service
        self.reward_service = reward_service
    
    async def perform_awakening(self, user_id: int) -> AwakeningResult:
        """
        Initiates daily Awakening ritual.
        
        Process:
        1. Check if already completed today
        2. Generate personalized quests
        3. Award Shadow Key
        4. Track completion
        """
        
    async def check_awakening_status(self, user_id: int) -> AwakeningStatus:
        """
        Returns current Awakening status for the day.
        """
```

### DailyLoginService

**Purpose**: Manages daily login rewards and streak tracking.

**Responsibilities**:
- Login streak calculation
- Reward tier determination
- Reward distribution
- Streak reset logic

**Key Methods**:

```python
class DailyLoginService:
    def __init__(self,
                 user_repo: UserRepository,
                 reward_service: RewardService):
        self.user_repo = user_repo
        self.reward_service = reward_service
    
    async def process_daily_login(self, user_id: int) -> LoginReward:
        """
        Processes daily login and distributes rewards.
        
        Logic:
        1. Calculate days since last login
        2. Update or reset streak
        3. Determine reward tier
        4. Distribute rewards
        5. Update login timestamp
        """
        
    async def get_login_status(self, user_id: int) -> LoginStatus:
        """
        Returns current login streak and next reward information.
        """
```

## V1 Feature Re-implementation Services

### MovementLoggingService

**Purpose**: Re-implements V1 movement logging with improved architecture.

**Responsibilities**:
- Rep validation and logging
- XP calculation and distribution
- Movement tracking
- Performance analytics

**Key Methods**:

```python
class MovementLoggingService:
    async def log_movement(self, user_id: int, movement_id: int, reps: int) -> LogResult:
        """
        Logs movement reps and calculates XP rewards.
        
        Enhanced from V1 with:
        - Better validation
        - Improved XP calculations
        - Real-time Aura updates
        - Performance tracking
        """
```

### IncursionService

**Purpose**: Re-implements V1 Incursion system with V2 architecture.

**Responsibilities**:
- Group challenge management
- Participant coordination
- Progress tracking
- Reward distribution

**Key Methods**:

```python
class IncursionService:
    async def create_incursion(self, creator_id: int, config: IncursionConfig) -> Incursion:
        """
        Creates new group Incursion challenge.
        """
        
    async def join_incursion(self, user_id: int, incursion_id: int) -> JoinResult:
        """
        Adds user to existing Incursion.
        """
```

## Service Integration Patterns

### Transaction Management
```python
@transactional
async def complex_operation(self, user_id: int) -> Result:
    """
    Services use decorators for transaction management.
    Ensures atomicity across multiple repository operations.
    """
```

### Error Handling
```python
try:
    result = await self.some_operation()
except DomainException as e:
    logger.error(f"Business logic error: {e}")
    await self.sentry_service.capture_exception(e)
    raise ServiceException(f"Operation failed: {e.message}")
```

### Caching Integration
```python
@cached(ttl=300)  # 5-minute cache
async def get_skill_tree_library(self) -> SkillTreeLibrary:
    """
    Services integrate with Redis caching for performance.
    """
```

## Testing Strategy

### Unit Testing
- Mock all dependencies (repositories, external services)
- Test business logic in isolation
- Comprehensive edge case coverage

### Integration Testing
- Test service interactions with real database
- Verify transaction behavior
- Test error handling and rollback scenarios

### Performance Testing
- Load testing for high-traffic services
- Cache effectiveness validation
- Database query optimization verification

---
*This service design provides a clean, maintainable, and testable foundation for all GateGrind V2 business logic while supporting both new features and V1 re-implementation.*