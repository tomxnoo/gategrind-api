# Database Schema

## Overview

The GateGrind V2 database schema is implemented using **SQLAlchemy models**, providing a Python-native way to define tables, relationships, and constraints. The schema supports both V1 feature re-implementation and new V2 game systems.

## Core Entities

### Ascendant (User Profile)

The central entity representing a user in the GateGrind system.

```python
import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Ascendant(Base):
    __tablename__ = 'ascendants'
    
    # Primary identification
    id = Column(Integer, primary_key=True)
    discord_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String)
    
    # Core progression
    level = Column(Integer, default=1)
    global_xp = Column(Integer, default=0)
    
    # Stat points (earned through milestones)
    strength_points = Column(Integer, default=0)
    endurance_points = Column(Integer, default=0)
    technique_points = Column(Integer, default=0)
    
    # XP management
    rested_xp_pool = Column(Integer, default=0)
    
    # Power level system
    aura = Column(Integer, default=0, index=True)
    
    # Daily engagement
    last_login = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    stats = relationship("Stat", back_populates="ascendant", uselist=False)
    skill_progress = relationship("UserSkillProgress", back_populates="ascendant")
    quests = relationship("Quest", back_populates="ascendant")
    dungeon_keys = relationship("DungeonKey", back_populates="ascendant")
    dungeon_progress = relationship("DungeonProgress", back_populates="ascendant", uselist=False)
```

### Stat (Individual Stat Progression)

Tracks individual stat levels and experience for each user.

```python
class Stat(Base):
    __tablename__ = 'stats'
    
    id = Column(Integer, primary_key=True)
    ascendant_id = Column(Integer, ForeignKey('ascendants.id'), nullable=False)
    
    # Strength progression
    str_level = Column(Integer, default=1)
    str_xp = Column(Integer, default=0)
    
    # Endurance progression
    end_level = Column(Integer, default=1)
    end_xp = Column(Integer, default=0)
    
    # Technique progression
    tech_level = Column(Integer, default=1)
    tech_xp = Column(Integer, default=0)
    
    # Relationships
    ascendant = relationship("Ascendant", back_populates="stats")
```

## Movement & Skill System

### MovementCategory (Content Organization)

Organizes movements into logical categories (e.g., "Push", "Pull", "Core").

```python
class MovementCategory(Base):
    __tablename__ = 'movement_categories'
    
    id = Column(String, primary_key=True)  # e.g., "PUSH_VERTICAL"
    name = Column(String, nullable=False)  # e.g., "Vertical Push"
    description = Column(String)
    
    # Relationships
    skill_nodes = relationship("SkillTreeNode", back_populates="category")
```

### SkillTreeNode (Skill Tree Structure)

Defines the skill tree structure with unlock requirements.

```python
class SkillTreeNode(Base):
    __tablename__ = 'skill_tree_nodes'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(String, ForeignKey('movement_categories.id'), nullable=False)
    
    # Node definition
    level = Column(Integer, nullable=False)  # Position in skill tree
    name = Column(String, nullable=False)
    description = Column(String)
    
    # Unlock requirements
    required_ascendant_level = Column(Integer, default=1)
    required_str_points = Column(Integer, default=0)
    required_end_points = Column(Integer, default=0)
    required_tech_points = Column(Integer, default=0)
    
    # Relationships
    category = relationship("MovementCategory", back_populates="skill_nodes")
    movements = relationship("Movement", back_populates="skill_node")
    user_progress = relationship("UserSkillProgress", back_populates="skill_node")
```

### Movement (Individual Exercises)

Specific exercises within skill tree nodes.

```python
class Movement(Base):
    __tablename__ = 'movements'
    
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('skill_tree_nodes.id'), nullable=False)
    
    name = Column(String, nullable=False)
    xp_per_rep = Column(Integer, default=1)
    
    # Relationships
    skill_node = relationship("SkillTreeNode", back_populates="movements")
```

### UserSkillProgress (User Unlocks)

Tracks which skill nodes each user has unlocked.

```python
class UserSkillProgress(Base):
    __tablename__ = 'user_skill_progress'
    
    ascendant_id = Column(Integer, ForeignKey('ascendants.id'), primary_key=True)
    node_id = Column(Integer, ForeignKey('skill_tree_nodes.id'), primary_key=True)
    unlocked_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    ascendant = relationship("Ascendant", back_populates="skill_progress")
    skill_node = relationship("SkillTreeNode", back_populates="user_progress")
```

## Quest & Challenge System

### Quest (Dynamic Content)

Represents generated quests from various sources.

```python
class Quest(Base):
    __tablename__ = 'quests'
    
    id = Column(Integer, primary_key=True)
    ascendant_id = Column(Integer, ForeignKey('ascendants.id'), nullable=False)
    
    # Quest definition
    title = Column(String, nullable=False)
    description = Column(String)
    source = Column(String, nullable=False)  # 'Awakening', 'Dungeon', 'Incursion'
    status = Column(String, default='active')  # 'active', 'completed', 'expired'
    
    # Quest parameters (JSON or separate fields)
    target_movement = Column(String)  # Movement name or category
    target_reps = Column(Integer)
    reward_xp = Column(Integer)
    reward_items = Column(String)  # JSON string for complex rewards
    
    # Timing
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    ascendant = relationship("Ascendant", back_populates="quests")
```

## Dungeon System

### DungeonKey (Entry Tokens)

Tracks Shadow Keys and other dungeon entry tokens.

```python
class DungeonKey(Base):
    __tablename__ = 'dungeon_keys'
    
    id = Column(Integer, primary_key=True)
    ascendant_id = Column(Integer, ForeignKey('ascendants.id'), nullable=False)
    
    key_type = Column(String, default='shadow_key')
    quantity = Column(Integer, default=0)
    
    # Audit
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    ascendant = relationship("Ascendant", back_populates="dungeon_keys")
```

### DungeonProgress (Completion Tracking)

Tracks user progress through dungeon levels.

```python
class DungeonProgress(Base):
    __tablename__ = 'dungeon_progress'
    
    id = Column(Integer, primary_key=True)
    ascendant_id = Column(Integer, ForeignKey('ascendants.id'), nullable=False)
    
    highest_level_completed = Column(Integer, default=0)
    
    # Statistics
    total_attempts = Column(Integer, default=0)
    total_completions = Column(Integer, default=0)
    
    # Audit
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    ascendant = relationship("Ascendant", back_populates="dungeon_progress")
```

## Schema Design Principles

### 1. Normalization
- Proper normalization to reduce data redundancy
- Clear separation of concerns between entities
- Efficient relationship modeling

### 2. Performance Optimization
- Strategic indexing on frequently queried fields
- Composite indexes for complex queries
- Optimized foreign key relationships

### 3. Data Integrity
- Foreign key constraints ensure referential integrity
- Check constraints for business rule enforcement
- NOT NULL constraints for required fields

### 4. Audit Trail
- `created_at` and `updated_at` timestamps on all major entities
- Soft deletes where appropriate for data preservation
- Change tracking for critical business data

### 5. Scalability
- Integer primary keys for efficient joins
- Indexed fields for common query patterns
- Partitioning considerations for large tables

## Database Indexes

### Primary Indexes
```sql
-- User lookup optimization
CREATE INDEX idx_ascendants_discord_id ON ascendants(discord_id);
CREATE INDEX idx_ascendants_aura ON ascendants(aura);

-- Skill tree queries
CREATE INDEX idx_skill_nodes_category ON skill_tree_nodes(category_id);
CREATE INDEX idx_user_skill_progress_ascendant ON user_skill_progress(ascendant_id);

-- Quest management
CREATE INDEX idx_quests_ascendant_status ON quests(ascendant_id, status);
CREATE INDEX idx_quests_expires_at ON quests(expires_at);

-- Performance queries
CREATE INDEX idx_movements_node ON movements(node_id);
```

## Migration Strategy

### Initial Schema Creation
1. Create all base tables with relationships
2. Seed movement categories and skill tree structure
3. Create necessary indexes for performance

### Data Migration from V1
1. Map existing V1 user data to new Ascendant structure
2. Preserve existing progression and statistics
3. Initialize new fields with appropriate defaults

### Schema Evolution
1. Use Alembic for database migrations
2. Backward-compatible changes where possible
3. Data migration scripts for breaking changes

---
*This database schema provides a solid foundation for both V1 feature re-implementation and new V2 game systems while maintaining performance and data integrity.*