# Skill Tree Requirements Configuration Guide

## Overview

The GateGrind V2 skill tree system supports comprehensive configurable requirements for skill node unlocking. This document provides detailed information about the requirement configuration format, examples, and best practices.

## Requirement Types

### 1. Stat Point Requirements

Control access based on player stat allocations:

- `str_points`: Strength stat points required
- `end_points`: Endurance stat points required  
- `tech_points`: Technique stat points required

**Example:**
```python
requirements = SkillNodeRequirements(
    str_points=15,
    end_points=10,
    tech_points=8
)
```

### 2. Skill Point Requirements

Control access based on skill point investments:

- `skill_points`: General skill points required
- `strength_skill_points`: Strength-specific skill points
- `endurance_skill_points`: Endurance-specific skill points
- `technique_skill_points`: Technique-specific skill points

**Example:**
```python
requirements = SkillNodeRequirements(
    skill_points=25,
    strength_skill_points=5,
    endurance_skill_points=3,
    technique_skill_points=7
)
```

### 3. Level Requirements

- `min_ascendant_level`: Minimum ascendant level required

**Example:**
```python
requirements = SkillNodeRequirements(
    min_ascendant_level=10
)
```

### 4. Aura Score Requirements

- `min_aura_score`: Minimum aura score required

**Example:**
```python
requirements = SkillNodeRequirements(
    min_aura_score=500
)
```

### 5. Prerequisite Node Requirements

- `prerequisite_nodes`: List of skill node IDs that must be unlocked first

**Example:**
```python
requirements = SkillNodeRequirements(
    prerequisite_nodes=["power_awakening", "surge_initiate"]
)
```

### 6. Quest Requirements

- `required_quests`: List of quest IDs that must be completed

**Example:**
```python
requirements = SkillNodeRequirements(
    required_quests=["tutorial_complete", "first_boss_defeated"]
)
```

### 7. Achievement Requirements

- `required_achievements`: List of achievement IDs that must be earned

**Example:**
```python
requirements = SkillNodeRequirements(
    required_achievements=["speed_demon", "perfect_combo"]
)
```

## Configuration Examples

### Basic Node (Early Game)
```python
SkillNodeRequirements(
    str_points=5,
    end_points=0,
    tech_points=0,
    skill_points=10,
    min_ascendant_level=1,
    min_aura_score=0,
    prerequisite_nodes=[],
    required_quests=[],
    required_achievements=[]
)
```

### Intermediate Node (Mid Game)
```python
SkillNodeRequirements(
    str_points=20,
    end_points=15,
    tech_points=10,
    skill_points=50,
    strength_skill_points=8,
    endurance_skill_points=5,
    technique_skill_points=3,
    min_ascendant_level=15,
    min_aura_score=1000,
    prerequisite_nodes=["basic_strength", "basic_endurance"],
    required_quests=["mid_game_quest"],
    required_achievements=[]
)
```

### Advanced Node (End Game)
```python
SkillNodeRequirements(
    str_points=50,
    end_points=40,
    tech_points=35,
    skill_points=150,
    strength_skill_points=25,
    endurance_skill_points=20,
    technique_skill_points=18,
    min_ascendant_level=50,
    min_aura_score=5000,
    prerequisite_nodes=["master_strength", "master_endurance", "master_technique"],
    required_quests=["final_trial", "legendary_quest"],
    required_achievements=["grandmaster", "legend"]
)
```

### Specialized Node (Quest-Gated)
```python
SkillNodeRequirements(
    str_points=0,
    end_points=0,
    tech_points=0,
    skill_points=0,
    min_ascendant_level=1,
    min_aura_score=0,
    prerequisite_nodes=[],
    required_quests=["secret_questline_complete"],
    required_achievements=["hidden_achievement"]
)
```

## JSON Configuration Format

For dynamic loading, requirements can be stored in JSON format:

```json
{
  "power_awakening": {
    "str_points": 10,
    "end_points": 5,
    "tech_points": 0,
    "skill_points": 15,
    "strength_skill_points": 3,
    "endurance_skill_points": 1,
    "technique_skill_points": 0,
    "min_ascendant_level": 5,
    "min_aura_score": 100,
    "prerequisite_nodes": [],
    "required_quests": ["tutorial_complete"],
    "required_achievements": []
  },
  "surge_initiate": {
    "str_points": 15,
    "end_points": 10,
    "tech_points": 5,
    "skill_points": 25,
    "strength_skill_points": 5,
    "endurance_skill_points": 3,
    "technique_skill_points": 2,
    "min_ascendant_level": 8,
    "min_aura_score": 250,
    "prerequisite_nodes": ["power_awakening"],
    "required_quests": [],
    "required_achievements": []
  }
}
```

## Validation Rules

### Stat Points
- Must be non-negative integers
- Maximum value: 999
- Should follow logical progression (higher tier nodes require more points)

### Skill Points
- Must be non-negative integers
- Maximum value: 9999
- Specific skill points should not exceed general skill points

### Level Requirements
- Must be between 1 and 100
- Should increase with node tier/difficulty

### Aura Score
- Must be non-negative
- Maximum value: 999999
- Should correlate with node power level

### Prerequisites
- Node IDs must exist in the skill tree
- Cannot create circular dependencies
- Should form logical progression paths

### Quests and Achievements
- IDs must reference valid game content
- Should be achievable before the node becomes relevant

## Best Practices

### 1. Logical Progression
```python
# Good: Clear progression path
basic_node = SkillNodeRequirements(str_points=5, skill_points=10)
intermediate_node = SkillNodeRequirements(str_points=15, skill_points=30, prerequisite_nodes=["basic_node"])
advanced_node = SkillNodeRequirements(str_points=30, skill_points=75, prerequisite_nodes=["intermediate_node"])
```

### 2. Balanced Requirements
```python
# Good: Balanced across multiple stats
balanced_node = SkillNodeRequirements(
    str_points=20,
    end_points=15,
    tech_points=10,
    skill_points=45
)

# Avoid: Single-stat focus unless intentional
unbalanced_node = SkillNodeRequirements(str_points=50, end_points=0, tech_points=0)
```

### 3. Meaningful Gates
```python
# Good: Quest requirement for story-relevant node
story_node = SkillNodeRequirements(
    required_quests=["chapter_1_complete"],
    min_ascendant_level=10
)

# Good: Achievement requirement for optional powerful node
secret_node = SkillNodeRequirements(
    required_achievements=["perfect_run"],
    str_points=25,
    skill_points=50
)
```

### 4. Clear Dependencies
```python
# Good: Clear prerequisite chain
foundation = SkillNodeRequirements(str_points=5)
building_block = SkillNodeRequirements(str_points=10, prerequisite_nodes=["foundation"])
capstone = SkillNodeRequirements(str_points=20, prerequisite_nodes=["building_block"])
```

## API Integration

### Loading Requirements
```python
from app.application.services.skill_requirements_service import SkillRequirementsService

service = SkillRequirementsService()
requirements = await service.get_node_requirements("power_awakening")
```

### Updating Requirements
```python
new_requirements = SkillNodeRequirements(
    str_points=12,
    end_points=8,
    skill_points=20
)
await service.update_node_requirements("power_awakening", new_requirements)
```

### Validation
```python
from app.application.services.skill_requirements_validator import SkillRequirementsValidator

validator = SkillRequirementsValidator()
validation_results = validator.validate_requirements(requirements)
```

## Admin Interface

The web-based admin interface provides:

1. **View Requirements**: Browse all skill node requirements
2. **Edit Requirements**: Modify individual node requirements
3. **Validation**: Test requirement configurations
4. **Bulk Operations**: Update multiple nodes simultaneously
5. **Cache Management**: Clear cached requirements

Access the admin interface at: `/static/admin/skill_requirements.html`

## Caching Strategy

Requirements are cached using Redis with the following keys:
- `skill_requirements:{node_id}`: Individual node requirements
- `skill_requirements:all_nodes`: List of all available nodes

Cache TTL: 1 hour (configurable)

## Error Handling

Common validation errors and solutions:

### Invalid Stat Values
```
Error: "str_points must be between 0 and 999"
Solution: Ensure all stat point values are within valid ranges
```

### Circular Dependencies
```
Error: "Circular dependency detected in prerequisite chain"
Solution: Review prerequisite_nodes to ensure no circular references
```

### Missing Prerequisites
```
Error: "Prerequisite node 'unknown_node' does not exist"
Solution: Verify all prerequisite node IDs exist in the skill tree
```

### Invalid Quest/Achievement IDs
```
Error: "Quest 'invalid_quest' not found in game data"
Solution: Ensure quest and achievement IDs reference valid game content
```

## Migration Guide

When updating existing requirements:

1. **Backup Current Configuration**: Export current requirements before changes
2. **Validate New Configuration**: Use validation tools before applying
3. **Test in Development**: Verify changes work as expected
4. **Clear Cache**: Ensure cached data is refreshed after updates
5. **Monitor Player Impact**: Check for unintended progression blocking

## Performance Considerations

- Requirements are cached to minimize database queries
- Validation is performed asynchronously where possible
- Bulk operations are optimized for large-scale updates
- Cache invalidation is selective to minimize performance impact

## Security Notes

- Admin interface requires appropriate authentication
- Validation prevents malicious configuration values
- All updates are logged for audit purposes
- Rate limiting prevents abuse of update endpoints