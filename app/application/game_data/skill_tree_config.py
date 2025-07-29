"""
Skill Tree Configuration for GateGrind V2
==========================================

This module defines the complete skill tree structure with proper progression paths,
requirements, and costs for all skill tree nodes.

Key Progression Mechanics:
- Ascendant level up grants +1 to all 3 skill point types
- Skill points are DEDUCTED when unlocking nodes (cumulative cost)
- Stat requirements increase by 500 per level (0-500, 500-1000, 1000-1500, 1500-2000, 2000-2500)
- Level costs: 0, 3, 8, 15, 25 skill points (total: 51 to max a category)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class SkillNodeType(Enum):
    """Types of skill tree nodes for different progression patterns"""
    FOUNDATION = "foundation"      # Entry-level nodes (Level 1)
    PROGRESSION = "progression"    # Standard progression nodes (Levels 2-4)
    MASTERY = "mastery"           # High-level mastery nodes (Level 5)
    GATEWAY = "gateway"           # Nodes that unlock cross-category paths
    SPECIALIZATION = "specialization"  # Advanced technique specializations


@dataclass
class SkillNodeRequirements:
    """Requirements for unlocking a skill tree node"""
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

    def __post_init__(self):
        if self.prerequisite_nodes is None:
            self.prerequisite_nodes = []
        if self.required_quests is None:
            self.required_quests = []
        if self.required_achievements is None:
            self.required_achievements = []


@dataclass
class SkillTreeNode:
    """A single node in the skill tree"""
    id: str
    category_id: str
    level: int
    name: str
    description: str
    lore_text: str
    node_type: SkillNodeType
    requirements: SkillNodeRequirements
    rewards: Dict[str, Any]
    unlock_message: str


# =========================================================================
# SKILL TREE CONFIGURATION DICTIONARY
# =========================================================================

SKILL_TREE_CONFIG: Dict[str, List[SkillTreeNode]] = {}

# =========================================================================
# UPPER_DYNAMIC - Upper Dynamic (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["UPPER_DYNAMIC"] = [
    SkillTreeNode(
        id="upper_dynamic_1",
        category_id="UPPER_DYNAMIC",
        level=1,
        name="Upper Dynamic Foundation",
        description="Master the fundamentals of upper dynamic movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Upper Dynamic Foundation!"
    ),
    SkillTreeNode(
        id="upper_dynamic_2",
        category_id="UPPER_DYNAMIC",
        level=2,
        name="Upper Dynamic Development",
        description="Develop intermediate upper dynamic strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["upper_dynamic_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Upper Dynamic Development!"
    ),
    SkillTreeNode(
        id="upper_dynamic_3",
        category_id="UPPER_DYNAMIC",
        level=3,
        name="Upper Dynamic Proficiency",
        description="Reach proficiency in upper dynamic movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["upper_dynamic_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Upper Dynamic Proficiency!"
    ),
    SkillTreeNode(
        id="upper_dynamic_4",
        category_id="UPPER_DYNAMIC",
        level=4,
        name="Upper Dynamic Mastery",
        description="Master advanced upper dynamic techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["upper_dynamic_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Upper Dynamic Mastery!"
    ),
    SkillTreeNode(
        id="upper_dynamic_5",
        category_id="UPPER_DYNAMIC",
        level=5,
        name="Upper Dynamic Transcendence",
        description="Transcend the limits of upper dynamic power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["upper_dynamic_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Upper Dynamic Transcendence!"
    )
]
# =========================================================================
# MOBILITY_FLOW - Mobility Flow (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["MOBILITY_FLOW"] = [
    SkillTreeNode(
        id="mobility_flow_1",
        category_id="MOBILITY_FLOW",
        level=1,
        name="Mobility Flow Foundation",
        description="Master the fundamentals of mobility flow movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Mobility Flow Foundation!"
    ),
    SkillTreeNode(
        id="mobility_flow_2",
        category_id="MOBILITY_FLOW",
        level=2,
        name="Mobility Flow Development",
        description="Develop intermediate mobility flow strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["mobility_flow_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Mobility Flow Development!"
    ),
    SkillTreeNode(
        id="mobility_flow_3",
        category_id="MOBILITY_FLOW",
        level=3,
        name="Mobility Flow Proficiency",
        description="Reach proficiency in mobility flow movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["mobility_flow_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Mobility Flow Proficiency!"
    ),
    SkillTreeNode(
        id="mobility_flow_4",
        category_id="MOBILITY_FLOW",
        level=4,
        name="Mobility Flow Mastery",
        description="Master advanced mobility flow techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["mobility_flow_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Mobility Flow Mastery!"
    ),
    SkillTreeNode(
        id="mobility_flow_5",
        category_id="MOBILITY_FLOW",
        level=5,
        name="Mobility Flow Transcendence",
        description="Transcend the limits of mobility flow power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["mobility_flow_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Mobility Flow Transcendence!"
    )
]
# =========================================================================
# PULL_VERTICAL - Pull Vertical (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["PULL_VERTICAL"] = [
    SkillTreeNode(
        id="pull_vertical_1",
        category_id="PULL_VERTICAL",
        level=1,
        name="Pull Vertical Foundation",
        description="Master the fundamentals of pull vertical movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Pull Vertical Foundation!"
    ),
    SkillTreeNode(
        id="pull_vertical_2",
        category_id="PULL_VERTICAL",
        level=2,
        name="Pull Vertical Development",
        description="Develop intermediate pull vertical strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["pull_vertical_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Pull Vertical Development!"
    ),
    SkillTreeNode(
        id="pull_vertical_3",
        category_id="PULL_VERTICAL",
        level=3,
        name="Pull Vertical Proficiency",
        description="Reach proficiency in pull vertical movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["pull_vertical_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Pull Vertical Proficiency!"
    ),
    SkillTreeNode(
        id="pull_vertical_4",
        category_id="PULL_VERTICAL",
        level=4,
        name="Pull Vertical Mastery",
        description="Master advanced pull vertical techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["pull_vertical_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Pull Vertical Mastery!"
    ),
    SkillTreeNode(
        id="pull_vertical_5",
        category_id="PULL_VERTICAL",
        level=5,
        name="Pull Vertical Transcendence",
        description="Transcend the limits of pull vertical power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["pull_vertical_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Pull Vertical Transcendence!"
    )
]
# =========================================================================
# PUSH - Push (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["PUSH"] = [
    SkillTreeNode(
        id="push_1",
        category_id="PUSH",
        level=1,
        name="Push Foundation",
        description="Master the fundamentals of push movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Push Foundation!"
    ),
    SkillTreeNode(
        id="push_2",
        category_id="PUSH",
        level=2,
        name="Push Development",
        description="Develop intermediate push strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["push_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Push Development!"
    ),
    SkillTreeNode(
        id="push_3",
        category_id="PUSH",
        level=3,
        name="Push Proficiency",
        description="Reach proficiency in push movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["push_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Push Proficiency!"
    ),
    SkillTreeNode(
        id="push_4",
        category_id="PUSH",
        level=4,
        name="Push Mastery",
        description="Master advanced push techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["push_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Push Mastery!"
    ),
    SkillTreeNode(
        id="push_5",
        category_id="PUSH",
        level=5,
        name="Push Transcendence",
        description="Transcend the limits of push power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["push_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Push Transcendence!"
    )
]
# =========================================================================
# PULL - Pull (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["PULL"] = [
    SkillTreeNode(
        id="pull_1",
        category_id="PULL",
        level=1,
        name="Pull Foundation",
        description="Master the fundamentals of pull movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Pull Foundation!"
    ),
    SkillTreeNode(
        id="pull_2",
        category_id="PULL",
        level=2,
        name="Pull Development",
        description="Develop intermediate pull strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["pull_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Pull Development!"
    ),
    SkillTreeNode(
        id="pull_3",
        category_id="PULL",
        level=3,
        name="Pull Proficiency",
        description="Reach proficiency in pull movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["pull_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Pull Proficiency!"
    ),
    SkillTreeNode(
        id="pull_4",
        category_id="PULL",
        level=4,
        name="Pull Mastery",
        description="Master advanced pull techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["pull_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Pull Mastery!"
    ),
    SkillTreeNode(
        id="pull_5",
        category_id="PULL",
        level=5,
        name="Pull Transcendence",
        description="Transcend the limits of pull power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["pull_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Pull Transcendence!"
    )
]
# =========================================================================
# SQUAT - Squat (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["SQUAT"] = [
    SkillTreeNode(
        id="squat_1",
        category_id="SQUAT",
        level=1,
        name="Squat Foundation",
        description="Master the fundamentals of squat movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Squat Foundation!"
    ),
    SkillTreeNode(
        id="squat_2",
        category_id="SQUAT",
        level=2,
        name="Squat Development",
        description="Develop intermediate squat strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["squat_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Squat Development!"
    ),
    SkillTreeNode(
        id="squat_3",
        category_id="SQUAT",
        level=3,
        name="Squat Proficiency",
        description="Reach proficiency in squat movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["squat_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Squat Proficiency!"
    ),
    SkillTreeNode(
        id="squat_4",
        category_id="SQUAT",
        level=4,
        name="Squat Mastery",
        description="Master advanced squat techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["squat_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Squat Mastery!"
    ),
    SkillTreeNode(
        id="squat_5",
        category_id="SQUAT",
        level=5,
        name="Squat Transcendence",
        description="Transcend the limits of squat power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["squat_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Squat Transcendence!"
    )
]
# =========================================================================
# HINGE - Hinge (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["HINGE"] = [
    SkillTreeNode(
        id="hinge_1",
        category_id="HINGE",
        level=1,
        name="Hinge Foundation",
        description="Master the fundamentals of hinge movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Hinge Foundation!"
    ),
    SkillTreeNode(
        id="hinge_2",
        category_id="HINGE",
        level=2,
        name="Hinge Development",
        description="Develop intermediate hinge strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["hinge_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Hinge Development!"
    ),
    SkillTreeNode(
        id="hinge_3",
        category_id="HINGE",
        level=3,
        name="Hinge Proficiency",
        description="Reach proficiency in hinge movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["hinge_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Hinge Proficiency!"
    ),
    SkillTreeNode(
        id="hinge_4",
        category_id="HINGE",
        level=4,
        name="Hinge Mastery",
        description="Master advanced hinge techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["hinge_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Hinge Mastery!"
    ),
    SkillTreeNode(
        id="hinge_5",
        category_id="HINGE",
        level=5,
        name="Hinge Transcendence",
        description="Transcend the limits of hinge power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["hinge_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Hinge Transcendence!"
    )
]
# =========================================================================
# LUNGE - Lunge (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["LUNGE"] = [
    SkillTreeNode(
        id="lunge_1",
        category_id="LUNGE",
        level=1,
        name="Lunge Foundation",
        description="Master the fundamentals of lunge movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Lunge Foundation!"
    ),
    SkillTreeNode(
        id="lunge_2",
        category_id="LUNGE",
        level=2,
        name="Lunge Development",
        description="Develop intermediate lunge strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["lunge_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Lunge Development!"
    ),
    SkillTreeNode(
        id="lunge_3",
        category_id="LUNGE",
        level=3,
        name="Lunge Proficiency",
        description="Reach proficiency in lunge movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["lunge_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Lunge Proficiency!"
    ),
    SkillTreeNode(
        id="lunge_4",
        category_id="LUNGE",
        level=4,
        name="Lunge Mastery",
        description="Master advanced lunge techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["lunge_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Lunge Mastery!"
    ),
    SkillTreeNode(
        id="lunge_5",
        category_id="LUNGE",
        level=5,
        name="Lunge Transcendence",
        description="Transcend the limits of lunge power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["lunge_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Lunge Transcendence!"
    )
]
# =========================================================================
# ROTATION - Rotation (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["ROTATION"] = [
    SkillTreeNode(
        id="rotation_1",
        category_id="ROTATION",
        level=1,
        name="Rotation Foundation",
        description="Master the fundamentals of rotation movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Rotation Foundation!"
    ),
    SkillTreeNode(
        id="rotation_2",
        category_id="ROTATION",
        level=2,
        name="Rotation Development",
        description="Develop intermediate rotation strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["rotation_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Rotation Development!"
    ),
    SkillTreeNode(
        id="rotation_3",
        category_id="ROTATION",
        level=3,
        name="Rotation Proficiency",
        description="Reach proficiency in rotation movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["rotation_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Rotation Proficiency!"
    ),
    SkillTreeNode(
        id="rotation_4",
        category_id="ROTATION",
        level=4,
        name="Rotation Mastery",
        description="Master advanced rotation techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["rotation_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Rotation Mastery!"
    ),
    SkillTreeNode(
        id="rotation_5",
        category_id="ROTATION",
        level=5,
        name="Rotation Transcendence",
        description="Transcend the limits of rotation power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["rotation_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Rotation Transcendence!"
    )
]
# =========================================================================
# GAIT - Gait (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["GAIT"] = [
    SkillTreeNode(
        id="gait_1",
        category_id="GAIT",
        level=1,
        name="Gait Foundation",
        description="Master the fundamentals of gait movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Gait Foundation!"
    ),
    SkillTreeNode(
        id="gait_2",
        category_id="GAIT",
        level=2,
        name="Gait Development",
        description="Develop intermediate gait strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["gait_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Gait Development!"
    ),
    SkillTreeNode(
        id="gait_3",
        category_id="GAIT",
        level=3,
        name="Gait Proficiency",
        description="Reach proficiency in gait movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["gait_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Gait Proficiency!"
    ),
    SkillTreeNode(
        id="gait_4",
        category_id="GAIT",
        level=4,
        name="Gait Mastery",
        description="Master advanced gait techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["gait_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Gait Mastery!"
    ),
    SkillTreeNode(
        id="gait_5",
        category_id="GAIT",
        level=5,
        name="Gait Transcendence",
        description="Transcend the limits of gait power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["gait_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Gait Transcendence!"
    )
]
# =========================================================================
# LOADED_CARRY - Loaded Carry (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["LOADED_CARRY"] = [
    SkillTreeNode(
        id="loaded_carry_1",
        category_id="LOADED_CARRY",
        level=1,
        name="Loaded Carry Foundation",
        description="Master the fundamentals of loaded carry movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Loaded Carry Foundation!"
    ),
    SkillTreeNode(
        id="loaded_carry_2",
        category_id="LOADED_CARRY",
        level=2,
        name="Loaded Carry Development",
        description="Develop intermediate loaded carry strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["loaded_carry_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Loaded Carry Development!"
    ),
    SkillTreeNode(
        id="loaded_carry_3",
        category_id="LOADED_CARRY",
        level=3,
        name="Loaded Carry Proficiency",
        description="Reach proficiency in loaded carry movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["loaded_carry_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Loaded Carry Proficiency!"
    ),
    SkillTreeNode(
        id="loaded_carry_4",
        category_id="LOADED_CARRY",
        level=4,
        name="Loaded Carry Mastery",
        description="Master advanced loaded carry techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["loaded_carry_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Loaded Carry Mastery!"
    ),
    SkillTreeNode(
        id="loaded_carry_5",
        category_id="LOADED_CARRY",
        level=5,
        name="Loaded Carry Transcendence",
        description="Transcend the limits of loaded carry power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["loaded_carry_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Loaded Carry Transcendence!"
    )
]
# =========================================================================
# GROUND_MOVEMENT - Ground Movement (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["GROUND_MOVEMENT"] = [
    SkillTreeNode(
        id="ground_movement_1",
        category_id="GROUND_MOVEMENT",
        level=1,
        name="Ground Movement Foundation",
        description="Master the fundamentals of ground movement movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Ground Movement Foundation!"
    ),
    SkillTreeNode(
        id="ground_movement_2",
        category_id="GROUND_MOVEMENT",
        level=2,
        name="Ground Movement Development",
        description="Develop intermediate ground movement strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["ground_movement_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Ground Movement Development!"
    ),
    SkillTreeNode(
        id="ground_movement_3",
        category_id="GROUND_MOVEMENT",
        level=3,
        name="Ground Movement Proficiency",
        description="Reach proficiency in ground movement movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["ground_movement_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Ground Movement Proficiency!"
    ),
    SkillTreeNode(
        id="ground_movement_4",
        category_id="GROUND_MOVEMENT",
        level=4,
        name="Ground Movement Mastery",
        description="Master advanced ground movement techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["ground_movement_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Ground Movement Mastery!"
    ),
    SkillTreeNode(
        id="ground_movement_5",
        category_id="GROUND_MOVEMENT",
        level=5,
        name="Ground Movement Transcendence",
        description="Transcend the limits of ground movement power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["ground_movement_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Ground Movement Transcendence!"
    )
]
# =========================================================================
# BALLISTIC - Ballistic (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["BALLISTIC"] = [
    SkillTreeNode(
        id="ballistic_1",
        category_id="BALLISTIC",
        level=1,
        name="Ballistic Foundation",
        description="Master the fundamentals of ballistic movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Ballistic Foundation!"
    ),
    SkillTreeNode(
        id="ballistic_2",
        category_id="BALLISTIC",
        level=2,
        name="Ballistic Development",
        description="Develop intermediate ballistic strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["ballistic_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Ballistic Development!"
    ),
    SkillTreeNode(
        id="ballistic_3",
        category_id="BALLISTIC",
        level=3,
        name="Ballistic Proficiency",
        description="Reach proficiency in ballistic movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["ballistic_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Ballistic Proficiency!"
    ),
    SkillTreeNode(
        id="ballistic_4",
        category_id="BALLISTIC",
        level=4,
        name="Ballistic Mastery",
        description="Master advanced ballistic techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["ballistic_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Ballistic Mastery!"
    ),
    SkillTreeNode(
        id="ballistic_5",
        category_id="BALLISTIC",
        level=5,
        name="Ballistic Transcendence",
        description="Transcend the limits of ballistic power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["ballistic_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Ballistic Transcendence!"
    )
]
# =========================================================================
# PLYOMETRIC - Plyometric (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["PLYOMETRIC"] = [
    SkillTreeNode(
        id="plyometric_1",
        category_id="PLYOMETRIC",
        level=1,
        name="Plyometric Foundation",
        description="Master the fundamentals of plyometric movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Plyometric Foundation!"
    ),
    SkillTreeNode(
        id="plyometric_2",
        category_id="PLYOMETRIC",
        level=2,
        name="Plyometric Development",
        description="Develop intermediate plyometric strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["plyometric_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Plyometric Development!"
    ),
    SkillTreeNode(
        id="plyometric_3",
        category_id="PLYOMETRIC",
        level=3,
        name="Plyometric Proficiency",
        description="Reach proficiency in plyometric movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["plyometric_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Plyometric Proficiency!"
    ),
    SkillTreeNode(
        id="plyometric_4",
        category_id="PLYOMETRIC",
        level=4,
        name="Plyometric Mastery",
        description="Master advanced plyometric techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["plyometric_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Plyometric Mastery!"
    ),
    SkillTreeNode(
        id="plyometric_5",
        category_id="PLYOMETRIC",
        level=5,
        name="Plyometric Transcendence",
        description="Transcend the limits of plyometric power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["plyometric_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Plyometric Transcendence!"
    )
]
# =========================================================================
# GRIP - Grip (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["GRIP"] = [
    SkillTreeNode(
        id="grip_1",
        category_id="GRIP",
        level=1,
        name="Grip Foundation",
        description="Master the fundamentals of grip movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Grip Foundation!"
    ),
    SkillTreeNode(
        id="grip_2",
        category_id="GRIP",
        level=2,
        name="Grip Development",
        description="Develop intermediate grip strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["grip_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Grip Development!"
    ),
    SkillTreeNode(
        id="grip_3",
        category_id="GRIP",
        level=3,
        name="Grip Proficiency",
        description="Reach proficiency in grip movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["grip_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Grip Proficiency!"
    ),
    SkillTreeNode(
        id="grip_4",
        category_id="GRIP",
        level=4,
        name="Grip Mastery",
        description="Master advanced grip techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["grip_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Grip Mastery!"
    ),
    SkillTreeNode(
        id="grip_5",
        category_id="GRIP",
        level=5,
        name="Grip Transcendence",
        description="Transcend the limits of grip power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["grip_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Grip Transcendence!"
    )
]
# =========================================================================
# CORE - Core (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["CORE"] = [
    SkillTreeNode(
        id="core_1",
        category_id="CORE",
        level=1,
        name="Core Foundation",
        description="Master the fundamentals of core movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Core Foundation!"
    ),
    SkillTreeNode(
        id="core_2",
        category_id="CORE",
        level=2,
        name="Core Development",
        description="Develop intermediate core strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["core_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Core Development!"
    ),
    SkillTreeNode(
        id="core_3",
        category_id="CORE",
        level=3,
        name="Core Proficiency",
        description="Reach proficiency in core movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["core_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Core Proficiency!"
    ),
    SkillTreeNode(
        id="core_4",
        category_id="CORE",
        level=4,
        name="Core Mastery",
        description="Master advanced core techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["core_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Core Mastery!"
    ),
    SkillTreeNode(
        id="core_5",
        category_id="CORE",
        level=5,
        name="Core Transcendence",
        description="Transcend the limits of core power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["core_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Core Transcendence!"
    )
]
# =========================================================================
# FLEXIBILITY - Flexibility (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["FLEXIBILITY"] = [
    SkillTreeNode(
        id="flexibility_1",
        category_id="FLEXIBILITY",
        level=1,
        name="Flexibility Foundation",
        description="Master the fundamentals of flexibility movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Flexibility Foundation!"
    ),
    SkillTreeNode(
        id="flexibility_2",
        category_id="FLEXIBILITY",
        level=2,
        name="Flexibility Development",
        description="Develop intermediate flexibility strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["flexibility_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Flexibility Development!"
    ),
    SkillTreeNode(
        id="flexibility_3",
        category_id="FLEXIBILITY",
        level=3,
        name="Flexibility Proficiency",
        description="Reach proficiency in flexibility movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["flexibility_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Flexibility Proficiency!"
    ),
    SkillTreeNode(
        id="flexibility_4",
        category_id="FLEXIBILITY",
        level=4,
        name="Flexibility Mastery",
        description="Master advanced flexibility techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["flexibility_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Flexibility Mastery!"
    ),
    SkillTreeNode(
        id="flexibility_5",
        category_id="FLEXIBILITY",
        level=5,
        name="Flexibility Transcendence",
        description="Transcend the limits of flexibility power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["flexibility_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Flexibility Transcendence!"
    )
]
# =========================================================================
# BALANCE - Balance (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["BALANCE"] = [
    SkillTreeNode(
        id="balance_1",
        category_id="BALANCE",
        level=1,
        name="Balance Foundation",
        description="Master the fundamentals of balance movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Balance Foundation!"
    ),
    SkillTreeNode(
        id="balance_2",
        category_id="BALANCE",
        level=2,
        name="Balance Development",
        description="Develop intermediate balance strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["balance_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Balance Development!"
    ),
    SkillTreeNode(
        id="balance_3",
        category_id="BALANCE",
        level=3,
        name="Balance Proficiency",
        description="Reach proficiency in balance movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["balance_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Balance Proficiency!"
    ),
    SkillTreeNode(
        id="balance_4",
        category_id="BALANCE",
        level=4,
        name="Balance Mastery",
        description="Master advanced balance techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["balance_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Balance Mastery!"
    ),
    SkillTreeNode(
        id="balance_5",
        category_id="BALANCE",
        level=5,
        name="Balance Transcendence",
        description="Transcend the limits of balance power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["balance_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Balance Transcendence!"
    )
]
# =========================================================================
# COORDINATION - Coordination (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["COORDINATION"] = [
    SkillTreeNode(
        id="coordination_1",
        category_id="COORDINATION",
        level=1,
        name="Coordination Foundation",
        description="Master the fundamentals of coordination movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Coordination Foundation!"
    ),
    SkillTreeNode(
        id="coordination_2",
        category_id="COORDINATION",
        level=2,
        name="Coordination Development",
        description="Develop intermediate coordination strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["coordination_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Coordination Development!"
    ),
    SkillTreeNode(
        id="coordination_3",
        category_id="COORDINATION",
        level=3,
        name="Coordination Proficiency",
        description="Reach proficiency in coordination movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["coordination_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Coordination Proficiency!"
    ),
    SkillTreeNode(
        id="coordination_4",
        category_id="COORDINATION",
        level=4,
        name="Coordination Mastery",
        description="Master advanced coordination techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["coordination_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Coordination Mastery!"
    ),
    SkillTreeNode(
        id="coordination_5",
        category_id="COORDINATION",
        level=5,
        name="Coordination Transcendence",
        description="Transcend the limits of coordination power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["coordination_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Coordination Transcendence!"
    )
]
# =========================================================================
# REACTION - Reaction (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["REACTION"] = [
    SkillTreeNode(
        id="reaction_1",
        category_id="REACTION",
        level=1,
        name="Reaction Foundation",
        description="Master the fundamentals of reaction movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Reaction Foundation!"
    ),
    SkillTreeNode(
        id="reaction_2",
        category_id="REACTION",
        level=2,
        name="Reaction Development",
        description="Develop intermediate reaction strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["reaction_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Reaction Development!"
    ),
    SkillTreeNode(
        id="reaction_3",
        category_id="REACTION",
        level=3,
        name="Reaction Proficiency",
        description="Reach proficiency in reaction movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["reaction_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Reaction Proficiency!"
    ),
    SkillTreeNode(
        id="reaction_4",
        category_id="REACTION",
        level=4,
        name="Reaction Mastery",
        description="Master advanced reaction techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["reaction_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Reaction Mastery!"
    ),
    SkillTreeNode(
        id="reaction_5",
        category_id="REACTION",
        level=5,
        name="Reaction Transcendence",
        description="Transcend the limits of reaction power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["reaction_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Reaction Transcendence!"
    )
]
# =========================================================================
# AGILITY - Agility (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["AGILITY"] = [
    SkillTreeNode(
        id="agility_1",
        category_id="AGILITY",
        level=1,
        name="Agility Foundation",
        description="Master the fundamentals of agility movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Agility Foundation!"
    ),
    SkillTreeNode(
        id="agility_2",
        category_id="AGILITY",
        level=2,
        name="Agility Development",
        description="Develop intermediate agility strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["agility_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Agility Development!"
    ),
    SkillTreeNode(
        id="agility_3",
        category_id="AGILITY",
        level=3,
        name="Agility Proficiency",
        description="Reach proficiency in agility movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["agility_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Agility Proficiency!"
    ),
    SkillTreeNode(
        id="agility_4",
        category_id="AGILITY",
        level=4,
        name="Agility Mastery",
        description="Master advanced agility techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["agility_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Agility Mastery!"
    ),
    SkillTreeNode(
        id="agility_5",
        category_id="AGILITY",
        level=5,
        name="Agility Transcendence",
        description="Transcend the limits of agility power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["agility_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Agility Transcendence!"
    )
]
# =========================================================================
# POWER - Power (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["POWER"] = [
    SkillTreeNode(
        id="power_1",
        category_id="POWER",
        level=1,
        name="Power Foundation",
        description="Master the fundamentals of power movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Power Foundation!"
    ),
    SkillTreeNode(
        id="power_2",
        category_id="POWER",
        level=2,
        name="Power Development",
        description="Develop intermediate power strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["power_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Power Development!"
    ),
    SkillTreeNode(
        id="power_3",
        category_id="POWER",
        level=3,
        name="Power Proficiency",
        description="Reach proficiency in power movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["power_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Power Proficiency!"
    ),
    SkillTreeNode(
        id="power_4",
        category_id="POWER",
        level=4,
        name="Power Mastery",
        description="Master advanced power techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["power_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Power Mastery!"
    ),
    SkillTreeNode(
        id="power_5",
        category_id="POWER",
        level=5,
        name="Power Transcendence",
        description="Transcend the limits of power power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["power_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Power Transcendence!"
    )
]
# =========================================================================
# SPEED - Speed (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["SPEED"] = [
    SkillTreeNode(
        id="speed_1",
        category_id="SPEED",
        level=1,
        name="Speed Foundation",
        description="Master the fundamentals of speed movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Speed Foundation!"
    ),
    SkillTreeNode(
        id="speed_2",
        category_id="SPEED",
        level=2,
        name="Speed Development",
        description="Develop intermediate speed strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["speed_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Speed Development!"
    ),
    SkillTreeNode(
        id="speed_3",
        category_id="SPEED",
        level=3,
        name="Speed Proficiency",
        description="Reach proficiency in speed movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["speed_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Speed Proficiency!"
    ),
    SkillTreeNode(
        id="speed_4",
        category_id="SPEED",
        level=4,
        name="Speed Mastery",
        description="Master advanced speed techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["speed_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Speed Mastery!"
    ),
    SkillTreeNode(
        id="speed_5",
        category_id="SPEED",
        level=5,
        name="Speed Transcendence",
        description="Transcend the limits of speed power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["speed_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Speed Transcendence!"
    )
]
# =========================================================================
# STRENGTH - Strength (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["STRENGTH"] = [
    SkillTreeNode(
        id="strength_1",
        category_id="STRENGTH",
        level=1,
        name="Strength Foundation",
        description="Master the fundamentals of strength movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Strength Foundation!"
    ),
    SkillTreeNode(
        id="strength_2",
        category_id="STRENGTH",
        level=2,
        name="Strength Development",
        description="Develop intermediate strength strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["strength_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Strength Development!"
    ),
    SkillTreeNode(
        id="strength_3",
        category_id="STRENGTH",
        level=3,
        name="Strength Proficiency",
        description="Reach proficiency in strength movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["strength_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Strength Proficiency!"
    ),
    SkillTreeNode(
        id="strength_4",
        category_id="STRENGTH",
        level=4,
        name="Strength Mastery",
        description="Master advanced strength techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["strength_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Strength Mastery!"
    ),
    SkillTreeNode(
        id="strength_5",
        category_id="STRENGTH",
        level=5,
        name="Strength Transcendence",
        description="Transcend the limits of strength power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["strength_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Strength Transcendence!"
    )
]
# =========================================================================
# ENDURANCE - Endurance (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["ENDURANCE"] = [
    SkillTreeNode(
        id="endurance_1",
        category_id="ENDURANCE",
        level=1,
        name="Endurance Foundation",
        description="Master the fundamentals of endurance movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Endurance Foundation!"
    ),
    SkillTreeNode(
        id="endurance_2",
        category_id="ENDURANCE",
        level=2,
        name="Endurance Development",
        description="Develop intermediate endurance strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["endurance_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Endurance Development!"
    ),
    SkillTreeNode(
        id="endurance_3",
        category_id="ENDURANCE",
        level=3,
        name="Endurance Proficiency",
        description="Reach proficiency in endurance movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["endurance_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Endurance Proficiency!"
    ),
    SkillTreeNode(
        id="endurance_4",
        category_id="ENDURANCE",
        level=4,
        name="Endurance Mastery",
        description="Master advanced endurance techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["endurance_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Endurance Mastery!"
    ),
    SkillTreeNode(
        id="endurance_5",
        category_id="ENDURANCE",
        level=5,
        name="Endurance Transcendence",
        description="Transcend the limits of endurance power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["endurance_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Endurance Transcendence!"
    )
]
# =========================================================================
# TECHNIQUE - Technique (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["TECHNIQUE"] = [
    SkillTreeNode(
        id="technique_1",
        category_id="TECHNIQUE",
        level=1,
        name="Technique Foundation",
        description="Master the fundamentals of technique movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Technique Foundation!"
    ),
    SkillTreeNode(
        id="technique_2",
        category_id="TECHNIQUE",
        level=2,
        name="Technique Development",
        description="Develop intermediate technique strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["technique_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Technique Development!"
    ),
    SkillTreeNode(
        id="technique_3",
        category_id="TECHNIQUE",
        level=3,
        name="Technique Proficiency",
        description="Reach proficiency in technique movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["technique_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Technique Proficiency!"
    ),
    SkillTreeNode(
        id="technique_4",
        category_id="TECHNIQUE",
        level=4,
        name="Technique Mastery",
        description="Master advanced technique techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["technique_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Technique Mastery!"
    ),
    SkillTreeNode(
        id="technique_5",
        category_id="TECHNIQUE",
        level=5,
        name="Technique Transcendence",
        description="Transcend the limits of technique power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["technique_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Technique Transcendence!"
    )
]
# =========================================================================
# TACTICAL - Tactical (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["TACTICAL"] = [
    SkillTreeNode(
        id="tactical_1",
        category_id="TACTICAL",
        level=1,
        name="Tactical Foundation",
        description="Master the fundamentals of tactical movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Tactical Foundation!"
    ),
    SkillTreeNode(
        id="tactical_2",
        category_id="TACTICAL",
        level=2,
        name="Tactical Development",
        description="Develop intermediate tactical strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["tactical_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Tactical Development!"
    ),
    SkillTreeNode(
        id="tactical_3",
        category_id="TACTICAL",
        level=3,
        name="Tactical Proficiency",
        description="Reach proficiency in tactical movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["tactical_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Tactical Proficiency!"
    ),
    SkillTreeNode(
        id="tactical_4",
        category_id="TACTICAL",
        level=4,
        name="Tactical Mastery",
        description="Master advanced tactical techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["tactical_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Tactical Mastery!"
    ),
    SkillTreeNode(
        id="tactical_5",
        category_id="TACTICAL",
        level=5,
        name="Tactical Transcendence",
        description="Transcend the limits of tactical power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["tactical_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Tactical Transcendence!"
    )
]
# =========================================================================
# DEFENSIVE - Defensive (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["DEFENSIVE"] = [
    SkillTreeNode(
        id="defensive_1",
        category_id="DEFENSIVE",
        level=1,
        name="Defensive Foundation",
        description="Master the fundamentals of defensive movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Defensive Foundation!"
    ),
    SkillTreeNode(
        id="defensive_2",
        category_id="DEFENSIVE",
        level=2,
        name="Defensive Development",
        description="Develop intermediate defensive strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["defensive_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Defensive Development!"
    ),
    SkillTreeNode(
        id="defensive_3",
        category_id="DEFENSIVE",
        level=3,
        name="Defensive Proficiency",
        description="Reach proficiency in defensive movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["defensive_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Defensive Proficiency!"
    ),
    SkillTreeNode(
        id="defensive_4",
        category_id="DEFENSIVE",
        level=4,
        name="Defensive Mastery",
        description="Master advanced defensive techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["defensive_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Defensive Mastery!"
    ),
    SkillTreeNode(
        id="defensive_5",
        category_id="DEFENSIVE",
        level=5,
        name="Defensive Transcendence",
        description="Transcend the limits of defensive power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["defensive_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Defensive Transcendence!"
    )
]
# =========================================================================
# OFFENSIVE - Offensive (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["OFFENSIVE"] = [
    SkillTreeNode(
        id="offensive_1",
        category_id="OFFENSIVE",
        level=1,
        name="Offensive Foundation",
        description="Master the fundamentals of offensive movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Offensive Foundation!"
    ),
    SkillTreeNode(
        id="offensive_2",
        category_id="OFFENSIVE",
        level=2,
        name="Offensive Development",
        description="Develop intermediate offensive strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["offensive_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Offensive Development!"
    ),
    SkillTreeNode(
        id="offensive_3",
        category_id="OFFENSIVE",
        level=3,
        name="Offensive Proficiency",
        description="Reach proficiency in offensive movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["offensive_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Offensive Proficiency!"
    ),
    SkillTreeNode(
        id="offensive_4",
        category_id="OFFENSIVE",
        level=4,
        name="Offensive Mastery",
        description="Master advanced offensive techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["offensive_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Offensive Mastery!"
    ),
    SkillTreeNode(
        id="offensive_5",
        category_id="OFFENSIVE",
        level=5,
        name="Offensive Transcendence",
        description="Transcend the limits of offensive power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["offensive_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Offensive Transcendence!"
    )
]
# =========================================================================
# RECOVERY - Recovery (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["RECOVERY"] = [
    SkillTreeNode(
        id="recovery_1",
        category_id="RECOVERY",
        level=1,
        name="Recovery Foundation",
        description="Master the fundamentals of recovery movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Recovery Foundation!"
    ),
    SkillTreeNode(
        id="recovery_2",
        category_id="RECOVERY",
        level=2,
        name="Recovery Development",
        description="Develop intermediate recovery strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["recovery_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Recovery Development!"
    ),
    SkillTreeNode(
        id="recovery_3",
        category_id="RECOVERY",
        level=3,
        name="Recovery Proficiency",
        description="Reach proficiency in recovery movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["recovery_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Recovery Proficiency!"
    ),
    SkillTreeNode(
        id="recovery_4",
        category_id="RECOVERY",
        level=4,
        name="Recovery Mastery",
        description="Master advanced recovery techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["recovery_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Recovery Mastery!"
    ),
    SkillTreeNode(
        id="recovery_5",
        category_id="RECOVERY",
        level=5,
        name="Recovery Transcendence",
        description="Transcend the limits of recovery power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["recovery_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Recovery Transcendence!"
    )
]
# =========================================================================
# INJURY_PREVENTION - Injury Prevention (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["INJURY_PREVENTION"] = [
    SkillTreeNode(
        id="injury_prevention_1",
        category_id="INJURY_PREVENTION",
        level=1,
        name="Injury Prevention Foundation",
        description="Master the fundamentals of injury prevention movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Injury Prevention Foundation!"
    ),
    SkillTreeNode(
        id="injury_prevention_2",
        category_id="INJURY_PREVENTION",
        level=2,
        name="Injury Prevention Development",
        description="Develop intermediate injury prevention strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["injury_prevention_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Injury Prevention Development!"
    ),
    SkillTreeNode(
        id="injury_prevention_3",
        category_id="INJURY_PREVENTION",
        level=3,
        name="Injury Prevention Proficiency",
        description="Reach proficiency in injury prevention movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["injury_prevention_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Injury Prevention Proficiency!"
    ),
    SkillTreeNode(
        id="injury_prevention_4",
        category_id="INJURY_PREVENTION",
        level=4,
        name="Injury Prevention Mastery",
        description="Master advanced injury prevention techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["injury_prevention_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Injury Prevention Mastery!"
    ),
    SkillTreeNode(
        id="injury_prevention_5",
        category_id="INJURY_PREVENTION",
        level=5,
        name="Injury Prevention Transcendence",
        description="Transcend the limits of injury prevention power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["injury_prevention_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Injury Prevention Transcendence!"
    )
]
# =========================================================================
# MENTAL - Mental (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["MENTAL"] = [
    SkillTreeNode(
        id="mental_1",
        category_id="MENTAL",
        level=1,
        name="Mental Foundation",
        description="Master the fundamentals of mental movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Mental Foundation!"
    ),
    SkillTreeNode(
        id="mental_2",
        category_id="MENTAL",
        level=2,
        name="Mental Development",
        description="Develop intermediate mental strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["mental_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Mental Development!"
    ),
    SkillTreeNode(
        id="mental_3",
        category_id="MENTAL",
        level=3,
        name="Mental Proficiency",
        description="Reach proficiency in mental movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["mental_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Mental Proficiency!"
    ),
    SkillTreeNode(
        id="mental_4",
        category_id="MENTAL",
        level=4,
        name="Mental Mastery",
        description="Master advanced mental techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["mental_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Mental Mastery!"
    ),
    SkillTreeNode(
        id="mental_5",
        category_id="MENTAL",
        level=5,
        name="Mental Transcendence",
        description="Transcend the limits of mental power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["mental_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Mental Transcendence!"
    )
]
# =========================================================================
# STRATEGIC - Strategic (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["STRATEGIC"] = [
    SkillTreeNode(
        id="strategic_1",
        category_id="STRATEGIC",
        level=1,
        name="Strategic Foundation",
        description="Master the fundamentals of strategic movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Strategic Foundation!"
    ),
    SkillTreeNode(
        id="strategic_2",
        category_id="STRATEGIC",
        level=2,
        name="Strategic Development",
        description="Develop intermediate strategic strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["strategic_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Strategic Development!"
    ),
    SkillTreeNode(
        id="strategic_3",
        category_id="STRATEGIC",
        level=3,
        name="Strategic Proficiency",
        description="Reach proficiency in strategic movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["strategic_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Strategic Proficiency!"
    ),
    SkillTreeNode(
        id="strategic_4",
        category_id="STRATEGIC",
        level=4,
        name="Strategic Mastery",
        description="Master advanced strategic techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["strategic_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Strategic Mastery!"
    ),
    SkillTreeNode(
        id="strategic_5",
        category_id="STRATEGIC",
        level=5,
        name="Strategic Transcendence",
        description="Transcend the limits of strategic power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["strategic_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Strategic Transcendence!"
    )
]
# =========================================================================
# COMPETITIVE - Competitive (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["COMPETITIVE"] = [
    SkillTreeNode(
        id="competitive_1",
        category_id="COMPETITIVE",
        level=1,
        name="Competitive Foundation",
        description="Master the fundamentals of competitive movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Competitive Foundation!"
    ),
    SkillTreeNode(
        id="competitive_2",
        category_id="COMPETITIVE",
        level=2,
        name="Competitive Development",
        description="Develop intermediate competitive strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["competitive_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Competitive Development!"
    ),
    SkillTreeNode(
        id="competitive_3",
        category_id="COMPETITIVE",
        level=3,
        name="Competitive Proficiency",
        description="Reach proficiency in competitive movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["competitive_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Competitive Proficiency!"
    ),
    SkillTreeNode(
        id="competitive_4",
        category_id="COMPETITIVE",
        level=4,
        name="Competitive Mastery",
        description="Master advanced competitive techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["competitive_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Competitive Mastery!"
    ),
    SkillTreeNode(
        id="competitive_5",
        category_id="COMPETITIVE",
        level=5,
        name="Competitive Transcendence",
        description="Transcend the limits of competitive power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["competitive_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Competitive Transcendence!"
    )
]
# =========================================================================
# FUNCTIONAL - Functional (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["FUNCTIONAL"] = [
    SkillTreeNode(
        id="functional_1",
        category_id="FUNCTIONAL",
        level=1,
        name="Functional Foundation",
        description="Master the fundamentals of functional movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Functional Foundation!"
    ),
    SkillTreeNode(
        id="functional_2",
        category_id="FUNCTIONAL",
        level=2,
        name="Functional Development",
        description="Develop intermediate functional strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["functional_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Functional Development!"
    ),
    SkillTreeNode(
        id="functional_3",
        category_id="FUNCTIONAL",
        level=3,
        name="Functional Proficiency",
        description="Reach proficiency in functional movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["functional_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Functional Proficiency!"
    ),
    SkillTreeNode(
        id="functional_4",
        category_id="FUNCTIONAL",
        level=4,
        name="Functional Mastery",
        description="Master advanced functional techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["functional_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Functional Mastery!"
    ),
    SkillTreeNode(
        id="functional_5",
        category_id="FUNCTIONAL",
        level=5,
        name="Functional Transcendence",
        description="Transcend the limits of functional power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["functional_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Functional Transcendence!"
    )
]
# =========================================================================
# SPORT_SPECIFIC - Sport Specific (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["SPORT_SPECIFIC"] = [
    SkillTreeNode(
        id="sport_specific_1",
        category_id="SPORT_SPECIFIC",
        level=1,
        name="Sport Specific Foundation",
        description="Master the fundamentals of sport specific movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Sport Specific Foundation!"
    ),
    SkillTreeNode(
        id="sport_specific_2",
        category_id="SPORT_SPECIFIC",
        level=2,
        name="Sport Specific Development",
        description="Develop intermediate sport specific strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["sport_specific_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Sport Specific Development!"
    ),
    SkillTreeNode(
        id="sport_specific_3",
        category_id="SPORT_SPECIFIC",
        level=3,
        name="Sport Specific Proficiency",
        description="Reach proficiency in sport specific movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["sport_specific_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Sport Specific Proficiency!"
    ),
    SkillTreeNode(
        id="sport_specific_4",
        category_id="SPORT_SPECIFIC",
        level=4,
        name="Sport Specific Mastery",
        description="Master advanced sport specific techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["sport_specific_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Sport Specific Mastery!"
    ),
    SkillTreeNode(
        id="sport_specific_5",
        category_id="SPORT_SPECIFIC",
        level=5,
        name="Sport Specific Transcendence",
        description="Transcend the limits of sport specific power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["sport_specific_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Sport Specific Transcendence!"
    )
]
# =========================================================================
# REHABILITATION - Rehabilitation (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["REHABILITATION"] = [
    SkillTreeNode(
        id="rehabilitation_1",
        category_id="REHABILITATION",
        level=1,
        name="Rehabilitation Foundation",
        description="Master the fundamentals of rehabilitation movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Rehabilitation Foundation!"
    ),
    SkillTreeNode(
        id="rehabilitation_2",
        category_id="REHABILITATION",
        level=2,
        name="Rehabilitation Development",
        description="Develop intermediate rehabilitation strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["rehabilitation_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Rehabilitation Development!"
    ),
    SkillTreeNode(
        id="rehabilitation_3",
        category_id="REHABILITATION",
        level=3,
        name="Rehabilitation Proficiency",
        description="Reach proficiency in rehabilitation movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["rehabilitation_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Rehabilitation Proficiency!"
    ),
    SkillTreeNode(
        id="rehabilitation_4",
        category_id="REHABILITATION",
        level=4,
        name="Rehabilitation Mastery",
        description="Master advanced rehabilitation techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["rehabilitation_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Rehabilitation Mastery!"
    ),
    SkillTreeNode(
        id="rehabilitation_5",
        category_id="REHABILITATION",
        level=5,
        name="Rehabilitation Transcendence",
        description="Transcend the limits of rehabilitation power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["rehabilitation_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Rehabilitation Transcendence!"
    )
]
# =========================================================================
# CORRECTIVE - Corrective (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["CORRECTIVE"] = [
    SkillTreeNode(
        id="corrective_1",
        category_id="CORRECTIVE",
        level=1,
        name="Corrective Foundation",
        description="Master the fundamentals of corrective movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Corrective Foundation!"
    ),
    SkillTreeNode(
        id="corrective_2",
        category_id="CORRECTIVE",
        level=2,
        name="Corrective Development",
        description="Develop intermediate corrective strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["corrective_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Corrective Development!"
    ),
    SkillTreeNode(
        id="corrective_3",
        category_id="CORRECTIVE",
        level=3,
        name="Corrective Proficiency",
        description="Reach proficiency in corrective movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["corrective_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Corrective Proficiency!"
    ),
    SkillTreeNode(
        id="corrective_4",
        category_id="CORRECTIVE",
        level=4,
        name="Corrective Mastery",
        description="Master advanced corrective techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["corrective_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Corrective Mastery!"
    ),
    SkillTreeNode(
        id="corrective_5",
        category_id="CORRECTIVE",
        level=5,
        name="Corrective Transcendence",
        description="Transcend the limits of corrective power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["corrective_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Corrective Transcendence!"
    )
]
# =========================================================================
# ADVANCED - Advanced (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["ADVANCED"] = [
    SkillTreeNode(
        id="advanced_1",
        category_id="ADVANCED",
        level=1,
        name="Advanced Foundation",
        description="Master the fundamentals of advanced movements",
        lore_text="Every great strength begins with a solid foundation.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Advanced Foundation!"
    ),
    SkillTreeNode(
        id="advanced_2",
        category_id="ADVANCED",
        level=2,
        name="Advanced Development",
        description="Develop intermediate advanced strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["advanced_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Advanced Development!"
    ),
    SkillTreeNode(
        id="advanced_3",
        category_id="ADVANCED",
        level=3,
        name="Advanced Proficiency",
        description="Reach proficiency in advanced movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["advanced_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Advanced Proficiency!"
    ),
    SkillTreeNode(
        id="advanced_4",
        category_id="ADVANCED",
        level=4,
        name="Advanced Mastery",
        description="Master advanced advanced techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["advanced_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Advanced Mastery!"
    ),
    SkillTreeNode(
        id="advanced_5",
        category_id="ADVANCED",
        level=5,
        name="Advanced Transcendence",
        description="Transcend the limits of advanced power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["advanced_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Advanced Transcendence!"
    )
]


# =========================================================================
# UTILITY FUNCTIONS
# =========================================================================

def get_node_by_id(node_id: str) -> Optional[SkillTreeNode]:
    """
    Get a skill tree node by its ID.
    
    Args:
        node_id: The ID of the node to find (e.g., "upper_dynamic_1")
        
    Returns:
        The SkillTreeNode if found, None otherwise
    """
    for category_nodes in SKILL_TREE_CONFIG.values():
        for node in category_nodes:
            if node.id == node_id:
                return node
    return None


def get_all_nodes() -> List[SkillTreeNode]:
    """
    Get all skill tree nodes across all categories.
    
    Returns:
        List of all SkillTreeNode objects
    """
    all_nodes = []
    for category_nodes in SKILL_TREE_CONFIG.values():
        all_nodes.extend(category_nodes)
    return all_nodes


def get_nodes_by_category(category_id: str) -> List[SkillTreeNode]:
    """
    Get all nodes for a specific category.
    
    Args:
        category_id: The category ID (e.g., "UPPER_DYNAMIC")
        
    Returns:
        List of SkillTreeNode objects for the category
    """
    return SKILL_TREE_CONFIG.get(category_id, [])