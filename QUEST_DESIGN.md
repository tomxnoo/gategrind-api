# Quest System Design Document
## Realm of Shadows - Awakening & Quest Generation

### Overview
This document defines the complete quest system design for the Realm of Shadows Discord bot, based on the user's detailed planning and requirements.

## Core Philosophy

### Training Methodology
- **Grease the Groove (GtG)**: High-frequency, sub-maximal training
- **Autoregulation**: Training intensity adapts to daily energy levels
- **Flexibility**: Works around unpredictable 3-shift work schedule
- **Goal**: Anime-like V-taper physique (wide shoulders/back, narrow waist)

### RPG Integration
- **Theme**: Dark fantasy "shadow warrior" aesthetic
- **Stats**: STR (Strength), END (Endurance), TECH (Technique)
- **Progression**: XP and stat gains from quest completion
- **Engagement**: Thematic quest names and descriptions

## Quest Tier System

### Tier 1: The Shadow's Practice (Common - 60%)
**Purpose**: Foundational volume and skill practice (pure GtG)
**Intensity**: Low (40-60% of max reps per set)
**Format**: "Accumulate X reps throughout the day"
**Target**: 40-60 total reps for given exercise
**Rewards**: Standard XP, +END

**Example**:
- **Name**: "Whispers of Strength"
- **Description**: "The shadows demand practice. Accumulate 50 Standard Push-ups throughout your day. Each set should feel easy, a mere echo of your true power."

### Tier 2: The Warrior's Trial (Uncommon - 30%)
**Purpose**: Technique focus and muscular endurance
**Intensity**: Moderate (feel the effort, but not to failure)
**Format**: Specific sets/reps with technical parameters
**Target**: 3-5 sets with quality focus
**Rewards**: Medium XP, significant +TECH, moderate +STR

**Example**:
- **Name**: "The Controlled Descent"
- **Description**: "True power is not just in the rise, but in the fall. Perform 4 sets of 5 Negative Pull-ups, focusing on a slow, 3-second descent for each rep."

### Tier 3: The Ascendant's Challenge (Rare - 10%)
**Purpose**: Drive hypertrophy and test limits
**Intensity**: High (pushing close to or to failure)
**Format**: "Perform X sets to near-failure" or "Achieve new Rep Max"
**Target**: 3-4 high-effort sets
**Rewards**: High XP, significant +STR, moderate +END

**Example**:
- **Name**: "Test of Might"
- **Description**: "The realm demands a show of force! Perform 3 sets of Pike Push-ups, pushing each set until you have only 1-2 reps left in the tank. Rest fully between sets."

## Daily Quest Generation

### Quest Layout (3-5 quests generated)
1. **Main Upper Body**: Random PUSH or PULL quest (any tier)
2. **Main Foundation**: Random LEGS or CORE quest (weighted toward Tier 1-2)
3. **Wildcard/V-Taper**: Technique quest (Tier 2) or ACCESSORY_SHOULDERS
4. **Optional Volume**: Tier 1 quests for different muscle groups
5. **Optional Volume**: Additional Tier 1 quest if generated

### Autoregulation System
Based on daily `!feeling [1-5]` command:

**Low Energy (1-2)**:
- Heavy weighting toward Tier 1 (Volume) and Tier 2 (Technique)
- Tier 3 probability reduced to ~0%
- Message: "The shadows advise practice, not battle. Focus on form today."

**High Energy (4-5)**:
- Increased Tier 3 probability (25-30%)
- Normal distribution for other tiers
- Message: "You feel powerful. Today is a good day to challenge your limits."

## Weekly Quest System

### Quest Types

#### Passive Quests (Background Tracking)
**Volume Vow**: "Accumulate X reps of specific exercise from completed Daily Quests"
- Example: "The Shadow's Tithe" - Accumulate 300 Push-ups this week

**Consistency Vow**: "Complete Daily Quest on X different days"
- Example: "The Unbroken Path" - Complete a Daily Quest on 5 different days

#### Active Quests (Conscious Challenge)
**Peak Strength Mandate**: "Set new Max Rep Record for specific exercise"
- Example: "Trial of Peak Strength" - Achieve new personal best

**Technique Mandate**: "Perform X sets of specific accessory exercise"
- Example: "The Sculptor's Discipline" - Complete 12 sets of Lateral Raises this week

### Generation Logic
**Weekly Reset**:
- 1-2 Passive Quests (Volume + Consistency)
- 1 Active Quest (Peak Strength OR Technique)
- User can have all Passive quests running, but only one Active quest

## Exercise Library Structure

### Movement Categories
- **PULL**: Path of Ascension (Back & Biceps)
- **PUSH_H**: Earthbreaker's Might (Chest & Triceps) 
- **PUSH_V**: The Titan's Shoulders (Shoulders & Upper Chest)
- **LEGS**: Root of Power (Legs & Glutes)
- **CORE**: The Iron Will (Abs & Core)
- **ACCESSORY_SHOULDERS**: The Sculptor's Art (Lateral Deltoids)

### Progression Paths
Each category contains multiple exercise progressions:
- Beginner → Intermediate → Advanced variations
- Specific rep ranges and form cues
- Thematic descriptions and flavor text

## Awakening System Integration

### Daily Awakening Ritual
1. **Energy Assessment**: User selects readiness level (1-5)
2. **Quest Generation**: System generates 3-5 quests based on energy
3. **Quest Selection**: User chooses one quest to activate
4. **Progress Tracking**: Quest completion tracked throughout day

### UI Flow
1. **Awakening Panel**: Shows if user has awakened today
2. **Energy Selection**: Buttons for readiness levels with descriptions
3. **Quest Unveiling**: Generated quests displayed with tier indicators
4. **Quest Activation**: User selects and activates chosen quest

## Technical Implementation Requirements

### Data Structures
- `QuestParameters`: Tier, exercise, target, rewards
- `GeneratedQuest`: Complete quest with name, description, requirements
- `QuestSession`: Active quest tracking and progress
- `AwakeningStatus`: Daily awakening state and quest availability

### Core Functions
- `generate_awakening_session()`: Creates daily quest options
- `select_quest()`: Activates chosen quest
- `track_progress()`: Updates quest completion
- `calculate_rewards()`: XP and stat gains

### Database Schema
- `awakening_sessions`: Daily awakening records
- `awakening_quests`: Generated quest options
- `active_quests`: Currently active quest tracking
- `quest_history`: Completed quest records

## Success Metrics

### User Engagement
- 70%+ daily awakening completion rate
- 60%+ quest completion rate
- Consistent daily usage patterns

### System Performance
- Quest generation < 2 seconds
- Accurate progress tracking
- Reliable reward calculation
- Proper tier distribution

## Future Enhancements

### Shadow Labyrinths
- Multi-stage quest chains
- Branching narrative paths
- Enhanced rewards system
- Community collaboration elements

### AI-Powered Generation
- Personalized quest creation based on history
- Dynamic difficulty adjustment
- Contextual quest recommendations
- Advanced autoregulation algorithms