# RoS-TRAE Complete Movements Source of Truth

*Last Updated: 2024-12-19*  
*Version: 2.0 - Enhanced with Skill Node Unlock Requirements*

This document serves as the definitive source of truth for all movements, exercises, progression mechanics, and **skill node unlock requirements** in the RoS-TRAE (Realm of Strength - Training, Resilience, Ascension, Excellence) system.

## Table of Contents

1. [Movement System Architecture](#movement-system-architecture)
2. [Core 6 Unified Categories](#core-6-unified-categories)
3. [18 V2 Movement Categories](#18-v2-movement-categories)
4. [Movement Progressions by Category](#movement-progressions-by-category)
5. [Exercise Library Definitions](#exercise-library-definitions)
6. [**Skill Node Unlock Requirements**](#skill-node-unlock-requirements)
7. [Quest-Related Movements](#quest-related-movements)
8. [System Mechanics](#system-mechanics)
9. [Implementation Details](#implementation-details)
10. [Legacy Movement Mappings](#legacy-movement-mappings)

---

## Skill Node Unlock Requirements

### Overview

The RoS-TRAE skill tree system implements a comprehensive progression mechanism where each skill node has specific unlock requirements. Players must meet ALL requirements to unlock a node, and certain resources are deducted upon successful unlock.

### Requirement Types

#### 1. Stat Point Requirements (Checked, Not Deducted)
These represent the player's accumulated stat allocations and are checked but NOT deducted when unlocking nodes:

- **`str_points`**: Strength stat points required
- **`end_points`**: Endurance stat points required  
- **`tech_points`**: Technique stat points required

#### 2. Skill Point Costs (Deducted Upon Unlock)
These are the actual costs paid to unlock nodes and are DEDUCTED from the player's available skill points:

- **`skill_points`**: General skill points cost (legacy system)
- **`strength_skill_points`**: Strength-specific skill points cost
- **`endurance_skill_points`**: Endurance-specific skill points cost
- **`technique_skill_points`**: Technique-specific skill points cost

#### 3. Level and Progression Requirements

- **`min_ascendant_level`**: Minimum player ascendant level required
- **`prerequisite_nodes`**: List of skill node IDs that must be unlocked first

#### 4. Advanced Requirements

- **`min_aura_score`**: Minimum aura score requirement
- **`required_quests`**: List of quest IDs that must be completed
- **`required_achievements`**: List of achievement IDs that must be earned

### Progression Mechanics

#### Ascendant Level Benefits
- **Each ascendant level up grants +1 to ALL 3 skill point types** (STR, END, TECH)
- Ascendant levels gate access to higher-tier skill nodes

#### Skill Point Economics
- **Skill points are DEDUCTED when unlocking nodes** (cumulative cost system)
- **Total cost to max a category**: 51 skill points (0+3+8+15+25)
- **Stat point conversion**: 1 skill point = 150 stat points

#### Stat Requirement Scaling
Stat requirements increase by 500 per level:
- **Level 1**: 0-500 stat points
- **Level 2**: 500-1000 stat points  
- **Level 3**: 1000-1500 stat points
- **Level 4**: 1500-2000 stat points
- **Level 5**: 2000-2500 stat points

### Node Types and Progression Patterns

#### Foundation Nodes (Level 1)
- **Cost**: 0 skill points
- **Purpose**: Entry-level access to movement categories
- **Requirements**: Minimal (usually just ascendant level 1)

#### Progression Nodes (Levels 2-4)
- **Cost**: 3, 8, 15 skill points respectively
- **Purpose**: Standard advancement through movement mastery
- **Requirements**: Escalating stat and prerequisite requirements

#### Mastery Nodes (Level 5)
- **Cost**: 25 skill points
- **Purpose**: Ultimate mastery of movement categories
- **Requirements**: Highest stat requirements and multiple prerequisites

#### Gateway Nodes
- **Purpose**: Unlock cross-category progression paths
- **Requirements**: Often require nodes from multiple categories

#### Specialization Nodes
- **Purpose**: Advanced technique specializations
- **Requirements**: High mastery in specific areas

### Detailed Requirement Examples

#### PULL_VERTICAL Category Progression

**Level 1: Grip of Shadows**
```yaml
requirements:
  strength_stat: 0
  endurance_stat: 0
  technique_stat: 0
  strength_skill_points: 0
  endurance_skill_points: 0
  technique_skill_points: 0
  required_nodes: []
  min_ascendant_level: 1
```

**Level 2: Scapular Awakening**
```yaml
requirements:
  strength_stat: 75
  endurance_stat: 25
  technique_stat: 50
  strength_skill_points: 2
  endurance_skill_points: 0
  technique_skill_points: 1
  required_nodes: ["pull_vertical_1"]
  min_ascendant_level: 3
```

**Level 3: Negative Mastery**
```yaml
requirements:
  strength_stat: 200
  endurance_stat: 100
  technique_stat: 150
  strength_skill_points: 5
  endurance_skill_points: 1
  technique_skill_points: 2
  required_nodes: ["pull_vertical_2"]
  min_ascendant_level: 6
```

**Level 4: Ascendant's Rise**
```yaml
requirements:
  strength_stat: 375
  endurance_stat: 200
  technique_stat: 300
  strength_skill_points: 10
  endurance_skill_points: 3
  technique_skill_points: 2
  required_nodes: ["pull_vertical_3"]
  min_ascendant_level: 10
```

**Level 5: Master of Ascension**
```yaml
requirements:
  strength_stat: 600
  endurance_stat: 350
  technique_stat: 500
  strength_skill_points: 20
  endurance_skill_points: 3
  technique_skill_points: 2
  required_nodes: ["pull_vertical_4"]
  min_ascendant_level: 15
```

#### UPPER_DYNAMIC Category Progression

**Level 1: Power Awakening**
```yaml
requirements:
  str_points: 0
  end_points: 0
  tech_points: 0
  skill_points: 0
  strength_skill_points: 0
  endurance_skill_points: 0
  technique_skill_points: 0
  prerequisite_nodes: []
  min_ascendant_level: 1
```

**Level 2: Surge Initiate**
```yaml
requirements:
  str_points: 500
  end_points: 250
  tech_points: 250
  skill_points: 3
  strength_skill_points: 2
  endurance_skill_points: 0
  technique_skill_points: 1
  prerequisite_nodes: ["upper_dynamic_1"]
  min_ascendant_level: 4
```

**Level 3: Thunder Striker**
```yaml
requirements:
  str_points: 1000
  end_points: 500
  tech_points: 500
  skill_points: 8
  strength_skill_points: 5
  endurance_skill_points: 1
  technique_skill_points: 2
  prerequisite_nodes: ["upper_dynamic_2"]
  min_ascendant_level: 7
```

**Level 4: Storm Bringer**
```yaml
requirements:
  str_points: 1500
  end_points: 750
  tech_points: 750
  skill_points: 15
  strength_skill_points: 10
  endurance_skill_points: 2
  technique_skill_points: 3
  prerequisite_nodes: ["upper_dynamic_3"]
  min_ascendant_level: 10
```

**Level 5: Power Incarnate**
```yaml
requirements:
  str_points: 2000
  end_points: 1000
  tech_points: 1000
  skill_points: 25
  strength_skill_points: 18
  endurance_skill_points: 3
  technique_skill_points: 4
  prerequisite_nodes: ["upper_dynamic_4"]
  min_ascendant_level: 13
```

#### MOBILITY_FLOW Category Progression

**Level 1: Flow Awakening**
```yaml
requirements:
  str_points: 0
  end_points: 0
  tech_points: 0
  skill_points: 0
  strength_skill_points: 0
  endurance_skill_points: 0
  technique_skill_points: 0
  prerequisite_nodes: []
  min_ascendant_level: 1
```

**Level 2: Stream Walker**
```yaml
requirements:
  str_points: 25
  end_points: 50
  tech_points: 100
  skill_points: 3
  strength_skill_points: 0
  endurance_skill_points: 1
  technique_skill_points: 2
  prerequisite_nodes: ["mobility_flow_1"]
  min_ascendant_level: 3
```

**Level 3: River Dancer**
```yaml
requirements:
  str_points: 100
  end_points: 150
  tech_points: 250
  skill_points: 8
  strength_skill_points: 1
  endurance_skill_points: 2
  technique_skill_points: 5
  prerequisite_nodes: ["mobility_flow_2"]
  min_ascendant_level: 6
```

**Level 4: Torrent Master**
```yaml
requirements:
  str_points: 200
  end_points: 350
  tech_points: 450
  skill_points: 15
  strength_skill_points: 2
  endurance_skill_points: 3
  technique_skill_points: 10
  prerequisite_nodes: ["mobility_flow_3"]
  min_ascendant_level: 9
```

**Level 5: Flow Incarnate**
```yaml
requirements:
  str_points: 350
  end_points: 600
  tech_points: 750
  skill_points: 25
  strength_skill_points: 3
  endurance_skill_points: 5
  technique_skill_points: 17
  prerequisite_nodes: ["mobility_flow_4"]
  min_ascendant_level: 12
```

### Unlock Process

1. **Requirement Verification**: System checks ALL requirements are met
2. **Resource Deduction**: Skill points are deducted from player pools
3. **Node Activation**: Node becomes available with associated movements
4. **Reward Distribution**: Player receives node rewards (stat points, XP, abilities)
5. **Progression Update**: Player's skill tree state is updated

### Configuration Management

#### Requirement Configuration Format
```python
@dataclass
class SkillNodeRequirements:
    # Stat requirements (checked but not deducted)
    str_points: int = 0
    end_points: int = 0
    tech_points: int = 0
    
    # Skill point costs (deducted upon unlock)
    skill_points: int = 0
    strength_skill_points: int = 0
    endurance_skill_points: int = 0
    technique_skill_points: int = 0
    
    # Prerequisite nodes and level requirements
    prerequisite_nodes: List[str] = None
    min_ascendant_level: int = 1
    
    # Advanced requirements
    min_aura_score: int = 0
    required_quests: List[str] = None
    required_achievements: List[str] = None
```

#### JSON Configuration Example
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
    "prerequisite_nodes": ["foundation_strength"],
    "min_ascendant_level": 5,
    "min_aura_score": 100,
    "required_quests": ["complete_basic_training"],
    "required_achievements": ["first_pullup"]
  }
}
```

---

## Overview
This document serves as the definitive source of truth for all movements (exercises) in the RoS-TRAE (Realm of Shadows - Training, Resilience, Ascension, Evolution) system. The movement system is organized into a hierarchical structure with Core 6 Unified Categories expanding into 18 V2 Categories and 15+ additional specialized categories.

## Movement System Architecture

### Core 6 Unified Categories
The foundation of the movement system consists of 6 primary categories:

1. **PULL** - All pulling movements
2. **PUSH_H** - Horizontal pushing movements  
3. **PUSH_V** - Vertical pushing movements
4. **LEGS** - Lower body movements
5. **CORE** - Core stability and strength
6. **ACCESSORY_SHOULDERS** - Shoulder accessory work

### 18 V2 Categories (Expanded from Core 6)
Each Core 6 category expands into multiple specialized V2 categories:

#### From PULL:
- **PULL_VERTICAL** - Vertical Pulling (Primary Stat: STR)
- **PULL_HORIZONTAL** - Horizontal Pulling (Primary Stat: STR)  
- **PULL_UNILATERAL** - Unilateral Pulling (Primary Stat: TECH)

#### From PUSH_H:
- **PUSH_HORIZONTAL** - Horizontal Pushing (Primary Stat: STR)
- **PUSH_UNILATERAL** - Unilateral Pushing (Primary Stat: TECH)

#### From PUSH_V:
- **PUSH_VERTICAL** - Vertical Pushing (Primary Stat: STR)
- **UPPER_ISOMETRIC** - Isometric Holds Upper (Primary Stat: STR)

#### From LEGS:
- **SQUAT_BILATERAL** - Bilateral Squats (Primary Stat: STR)
- **SQUAT_UNILATERAL** - Unilateral Squats (Primary Stat: TECH)
- **HINGE_BILATERAL** - Bilateral Hip Hinge (Primary Stat: STR)
- **HINGE_UNILATERAL** - Unilateral Hip Hinge (Primary Stat: TECH)

#### From CORE:
- **CORE_STATIC** - Static Core (Primary Stat: STR)
- **CORE_DYNAMIC** - Dynamic Core (Primary Stat: END)
- **CORE_ROTATIONAL** - Rotational Core (Primary Stat: TECH)

#### From ACCESSORY_SHOULDERS:
- **ACCESSORY_SHOULDERS** - Shoulder Accessory Work (Primary Stat: TECH)

### 15+ Additional Specialized Categories
Beyond the core V2 categories, the system includes specialized movement categories:

- **UPPER_DYNAMIC** - Dynamic Upper Body Movements
- **LOWER_PLYOMETRIC** - Lower Body Plyometric Movements
- **UPPER_PLYOMETRIC** - Upper Body Plyometric Movements
- **FLEXIBILITY** - Flexibility and Stretching
- **MOBILITY_FLOW** - Movement Flow and Mobility
- **LOCOMOTION** - Locomotion Patterns
- **BALANCE** - Balance Training
- **COORDINATION** - Coordination Exercises
- **POWER** - Power Development
- **CARRY** - Loaded Carries
- **GRIP** - Grip Strength
- **POSTERIOR** - Posterior Chain
- **RECOVERY** - Recovery Movements
- **CARDIO** - Cardiovascular Training
- **HANDSTAND** - Handstand Progressions
- **BRIDGE** - Bridge Progressions

## Detailed Movement Progressions

### PULL_VERTICAL (Vertical Pulling)
**Quest Flavor: "Path of Ascension"**
**Description: "Rise above your limitations through the ancient art of vertical pulling"**

#### Level 1 - Foundation
- Dead Hang
- Assisted Pull-ups

#### Level 2 - First Ascent  
- Negative Pull-ups
- Band-Assisted Pull-ups
- Jumping Pull-ups

#### Level 3 - Competence
- Standard Pull-ups
- Chin-ups

#### Level 4 - Strength
- Wide-Grip Pull-ups
- Commando Pull-ups
- L-Sit Pull-ups

#### Level 5 - Mastery
- Weighted Pull-ups
- One-Arm Pull-up Progression
- Muscle-ups

### PULL_HORIZONTAL (Horizontal Pulling)
#### Level 1 - Foundation
- Incline Rows
- Table Rows

#### Level 2 - First Ascent
- Body Rows
- Ring Rows

#### Level 3 - Competence
- Horizontal Pull-ups
- Inverted Rows

#### Level 4 - Strength
- Weighted Ring Rows
- Archer Rows

#### Level 5 - Mastery
- Advanced Ring Rows
- Weighted Horizontal Pulls
- One-Arm Rows

### PULL_UNILATERAL (Unilateral Pulling)
#### Level 1 - Foundation
- Assisted Archer Pull-ups
- Single-Arm Hangs

#### Level 2 - First Ascent
- Single-Arm Negatives
- Uneven Pull-ups

#### Level 3 - Competence
- Archer Pull-ups
- Single-Arm Lat Pulls
- Typewriter Pull-ups

#### Level 4 - Strength
- One-Arm Pull-up Negatives
- Advanced Archer Variations

#### Level 5 - Mastery
- One-Arm Pull-ups
- One-Arm Chin-ups

### PUSH_HORIZONTAL (Horizontal Pushing)
**Quest Flavor: "Earthbreaker's Might"**
**Description: "Channel the earth's power through horizontal dominance"**

#### Level 1 - Foundation
- Wall Push-ups
- Incline Push-ups

#### Level 2 - First Ascent
- Knee Push-ups
- Standard Push-ups

#### Level 3 - Competence
- Diamond Push-ups
- Wide-Grip Push-ups

#### Level 4 - Strength
- Archer Push-ups
- One-Arm Push-up Progression

#### Level 5 - Mastery
- One-Arm Push-ups
- Planche Push-ups

### PUSH_UNILATERAL (Unilateral Pushing)
#### Level 1 - Foundation
- Single-Arm Wall Push-ups
- Assisted Archer Push-ups

#### Level 2 - First Ascent
- Uneven Push-ups
- Single-Arm Incline Push-ups

#### Level 3 - Competence
- Archer Push-ups
- Single-Arm Push-up Negatives

#### Level 4 - Strength
- Advanced Archer Variations
- One-Arm Push-up Progression

#### Level 5 - Mastery
- One-Arm Push-ups
- Single-Arm Handstand Push-ups

### PUSH_VERTICAL (Vertical Pushing)
**Quest Flavor: "Titan's Shoulders"**
**Description: "Ascend to godlike shoulder strength through vertical mastery"**

#### Level 1 - Foundation
- Wall Handstand Hold
- Chest-to-Wall Handstand

#### Level 2 - First Ascent
- Pike Push-ups
- Handstand Hold

#### Level 3 - Competence
- Handstand Push-ups
- Freestanding Handstand

#### Level 4 - Strength
- Deficit Handstand Push-ups
- One-Arm Handstand Hold

#### Level 5 - Mastery
- One-Arm Handstand Push-ups
- 90-Degree Push-ups

### UPPER_ISOMETRIC (Isometric Holds Upper)
#### Level 1 - Foundation
- Planche Lean
- Front Lever Tuck

#### Level 2 - First Ascent
- Tuck Planche
- Advanced Tuck Front Lever
- Back Lever Progression

#### Level 3 - Competence
- Advanced Tuck Planche
- Straddle Front Lever
- Back Lever

#### Level 4 - Strength
- Straddle Planche
- Full Front Lever
- Iron Cross Progression

#### Level 5 - Mastery
- Full Planche
- One-Arm Front Lever
- Iron Cross

### SQUAT_BILATERAL (Bilateral Squats)
**Quest Flavor: "Root of Power"**
**Description: "Ground yourself in the fundamental strength of the earth"**

#### Level 1 - Foundation
- Bodyweight Squats
- Box Squats

#### Level 2 - First Ascent
- Jump Squats
- Goblet Squats
- Sumo Squats

#### Level 3 - Competence
- Pistol Squat Progression
- Bulgarian Split Squats

#### Level 4 - Strength
- Jump Squats with Tuck
- Single-Leg Box Squats
- Weighted Squats

#### Level 5 - Mastery
- Pistol Squats
- Shrimp Squats
- Dragon Squats

### SQUAT_UNILATERAL (Unilateral Squats)
#### Level 1 - Foundation
- Assisted Pistol Squats
- Single-Leg Box Squats

#### Level 2 - First Ascent
- Pistol Squat Negatives
- Cossack Squats
- Lateral Lunges

#### Level 3 - Competence
- Pistol Squats
- Shrimp Squat Progression

#### Level 4 - Strength
- Advanced Pistol Variations
- Jumping Pistol Squats

#### Level 5 - Mastery
- Weighted Pistol Squats
- Shrimp Squats
- Dragon Squats

### HINGE_BILATERAL (Bilateral Hip Hinge)
#### Level 1 - Foundation
- Romanian Deadlifts
- Good Mornings

#### Level 2 - First Ascent
- Single-Leg Deadlifts
- Hip Thrusts
- Glute Bridges

#### Level 3 - Competence
- Nordic Curls Progression
- Single-Leg Hip Thrusts

#### Level 4 - Strength
- Nordic Curls
- Advanced Single-Leg Deadlifts

#### Level 5 - Mastery
- Full Nordic Curls
- Weighted Hip Thrusts
- Advanced Posterior Chain

### HINGE_UNILATERAL (Unilateral Hip Hinge)
#### Level 1 - Foundation
- Single-Leg Glute Bridges
- Single-Leg Hip Thrusts

#### Level 2 - First Ascent
- Single-Leg Deadlifts
- Single-Leg Good Mornings

#### Level 3 - Competence
- Advanced Single-Leg Deadlifts
- Curtsy Lunges

#### Level 4 - Strength
- Single-Leg Nordic Progression
- Weighted Single-Leg Deadlifts

#### Level 5 - Mastery
- Single-Leg Nordic Curls
- Advanced Unilateral Hinges

### CORE_STATIC (Static Core)
**Quest Flavor: "Iron Will"**
**Description: "Forge an unbreakable core through unwavering stillness"**

#### Level 1 - Foundation
- Plank
- Side Plank

#### Level 2 - First Ascent
- Extended Plank
- Single-Arm Plank
- Plank Up-Downs

#### Level 3 - Competence
- L-Sit Progression
- Hollow Body Hold
- V-Sit Progression

#### Level 4 - Strength
- L-Sit
- Advanced Hollow Body
- Human Flag Progression

#### Level 5 - Mastery
- Advanced L-Sit
- Human Flag
- Front Lever Progression

### CORE_DYNAMIC (Dynamic Core)
#### Level 1 - Foundation
- Crunches
- Bicycle Crunches

#### Level 2 - First Ascent
- Mountain Climbers
- Russian Twists
- Leg Raises

#### Level 3 - Competence
- Hanging Knee Raises
- Windshield Wipers
- Dragon Flags Progression

#### Level 4 - Strength
- Hanging Leg Raises
- Dragon Flags
- Advanced Core Flows

#### Level 5 - Mastery
- Advanced Dragon Flags
- Human Flag Dynamics
- Core Flow Mastery

### CORE_ROTATIONAL (Rotational Core)
#### Level 1 - Foundation
- Russian Twists
- Wood Chops

#### Level 2 - First Ascent
- Medicine Ball Slams
- Rotational Lunges
- Side Planks with Rotation

#### Level 3 - Competence
- Windshield Wipers
- Turkish Get-ups
- Rotational Power

#### Level 4 - Strength
- Advanced Windshield Wipers
- Single-Arm Turkish Get-ups

#### Level 5 - Mastery
- Rotational Flow Mastery
- Advanced Turkish Get-up Variations

### ACCESSORY_SHOULDERS (Shoulder Accessory Work)
**Quest Flavor: "Sculptor's Art"**
**Description: "Craft perfect shoulder mechanics through precise isolation"**

#### Level 1 - Foundation
- Wall Lateral Raise

#### Level 2 - First Ascent
- Water Bottle Lateral Raise

#### Level 3 - Competence
- Single-Arm Lateral Raise

### UPPER_DYNAMIC (Dynamic Upper Body)
#### Level 1 - Foundation
- Muscle-up Progression
- Kipping Pull-ups

#### Level 2 - First Ascent
- Assisted Muscle-ups
- Chest-to-Bar Pull-ups
- Ring Transitions

#### Level 3 - Competence
- Muscle-ups
- Ring Muscle-ups
- Bar Muscle-ups

#### Level 4 - Strength
- Weighted Muscle-ups
- Slow Muscle-ups
- Advanced Ring Work

#### Level 5 - Mastery
- One-Arm Muscle-up Progression
- Advanced Ring Sequences
- Freestyle Combinations

### LOWER_PLYOMETRIC (Lower Body Plyometric)
#### Level 1 - Foundation
- Jump Squats
- Box Jumps

#### Level 2 - First Ascent
- Broad Jumps
- Lateral Jumps
- Tuck Jumps

#### Level 3 - Competence
- Single-Leg Jumps
- Depth Jumps
- Reactive Jumps

#### Level 4 - Strength
- Advanced Plyometric Sequences
- Weighted Jump Squats

#### Level 5 - Mastery
- Elite Plyometric Combinations
- Sport-Specific Power

### UPPER_PLYOMETRIC (Upper Body Plyometric)
#### Level 1 - Foundation
- Clapping Push-ups
- Medicine Ball Throws

#### Level 2 - First Ascent
- Explosive Push-ups
- Plyometric Pull-ups
- Medicine Ball Slams

#### Level 3 - Competence
- Advanced Clapping Push-ups
- Explosive Muscle-ups

#### Level 4 - Strength
- Multiple Clap Push-ups
- Weighted Explosive Movements

#### Level 5 - Mastery
- Elite Upper Body Power
- Advanced Explosive Sequences

### FLEXIBILITY (Flexibility and Stretching)
#### Level 1 - Foundation
- Basic Stretching
- Hip Flexor Stretches

#### Level 2 - First Ascent
- Dynamic Stretching
- Shoulder Mobility
- Hip Circles

#### Level 3 - Competence
- Advanced Stretching
- PNF Stretching
- Active Flexibility

#### Level 4 - Strength
- Loaded Stretching
- Extreme Range of Motion
- Flexibility Flows

#### Level 5 - Mastery
- Contortion Basics
- Advanced Flexibility
- Mobility Mastery

### MOBILITY_FLOW (Movement Flow and Mobility)
#### Level 1 - Foundation
- Basic Flow Sequences
- Joint Mobility

#### Level 2 - First Ascent
- Animal Movements
- Crawling Patterns
- Flow Transitions

#### Level 3 - Competence
- Advanced Animal Flow
- Complex Movement Patterns

#### Level 4 - Strength
- Freestyle Flow
- Creative Movement
- Flow Combinations

#### Level 5 - Mastery
- Flow Mastery
- Advanced Creative Sequences
- Movement Art

## Quest-Related Movements

### Quest Tier System
Each movement category includes quest-specific variations organized by tier:

- **Practice Tier** - Foundation level movements for beginners
- **Trial Tier** - Intermediate challenges for developing practitioners  
- **Challenge Tier** - Advanced movements for experienced athletes

### Quest Movement Examples
Based on the exercise library, quest movements include specific variations with:
- **Base Reps/Duration**: Starting point for quest requirements
- **Difficulty Scaling**: Progressive increases based on user level
- **Equipment Requirements**: Bodyweight, minimal equipment, or advanced gear
- **Form Cues**: Detailed instruction for proper execution
- **Stat Rewards**: STR, END, TECH, or FLEX gains per completion

## Legacy Movement Mappings

The system maintains backward compatibility with legacy movement names:

- **push_up** → Modern push-up variations
- **squat** → Modern squat progressions  
- **burpee** → High-intensity compound movements
- **pull_up** → Vertical pulling progressions
- **plank** → Core static holds
- **lunge** → Unilateral leg movements

## XP and Stat Reward System

### XP Multipliers by Category
- **PULL_VERTICAL**: 1.2x
- **PULL_HORIZONTAL**: 1.1x  
- **PULL_UNILATERAL**: 1.3x
- **PUSH_HORIZONTAL**: 1.0x
- **PUSH_VERTICAL**: 1.1x
- **PUSH_UNILATERAL**: 1.2x
- **SQUAT_BILATERAL**: 1.0x
- **SQUAT_UNILATERAL**: 1.2x
- **UPPER_DYNAMIC**: 1.4x
- **MOBILITY_FLOW**: 1.1x

### Primary Stat Assignments
- **STR (Strength)**: PULL_VERTICAL, PULL_HORIZONTAL, PUSH_HORIZONTAL, PUSH_VERTICAL, SQUAT_BILATERAL, HINGE_BILATERAL, CORE_STATIC, UPPER_ISOMETRIC
- **END (Endurance)**: CORE_DYNAMIC, CARDIO, RECOVERY
- **TECH (Technique)**: PULL_UNILATERAL, PUSH_UNILATERAL, SQUAT_UNILATERAL, HINGE_UNILATERAL, CORE_ROTATIONAL, ACCESSORY_SHOULDERS, UPPER_DYNAMIC, MOBILITY_FLOW, BALANCE, COORDINATION
- **FLEX (Flexibility)**: FLEXIBILITY, MOBILITY_FLOW

### Level-Based XP Values
- **Level 1 (Foundation)**: 1.0 base XP
- **Level 2 (First Ascent)**: 1.5 base XP  
- **Level 3 (Competence)**: 2.0 base XP
- **Level 4 (Strength)**: 2.5 base XP
- **Level 5 (Mastery)**: 3.0 base XP

## Implementation Notes

### Database Structure
- Movements are stored with category associations
- Skill tree progression tracks unlock requirements
- XP calculations use category multipliers and level scaling
- Quest generation pulls from appropriate tier movements

### API Integration
- Movement categories accessible via `/api/v2/movements/categories`
- Individual movements via `/api/v2/movements/{movement_id}`
- Skill tree data via `/api/v2/skill-tree`
- Quest movements via quest generation endpoints

### Skill Tree Unlocking
- Stat point requirements increase per level
- Prerequisite nodes must be unlocked first
- Ascendant level gates access to higher tiers
- Skill points deducted upon successful unlock

This document represents the complete movement system as implemented in RoS-TRAE, serving as the authoritative reference for all exercise progressions, categorizations, and mechanical implementations.