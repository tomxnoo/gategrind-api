"""
Rebalanced Skill Tree Configuration for GateGrind V2
===================================================

This file contains the updated skill tree progression with balanced requirements
that create meaningful long-term progression and strategic skill point allocation.

Key Changes:
- Increased skill point costs: Level 5 nodes now require 25 skill points (3,750 stat points)
- Higher stat requirements: Level 5 nodes require 500-750 stat points
- Progressive difficulty curve that rewards long-term engagement
- Maintains strategic choice in skill point allocation across categories
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
    strength_stat: int = 0
    endurance_stat: int = 0
    technique_stat: int = 0
    
    # Skill point costs (deducted upon unlock)
    strength_skill_points: int = 0
    endurance_skill_points: int = 0
    technique_skill_points: int = 0
    
    # Prerequisite nodes (must be unlocked first)
    required_nodes: List[str] = None
    
    # Minimum ascendant level
    min_ascendant_level: int = 1

    def __post_init__(self):
        if self.required_nodes is None:
            self.required_nodes = []


@dataclass
class SkillTreeNode:
    """Complete skill tree node definition"""
    id: str
    category_id: str
    level: int
    name: str
    description: str
    lore_text: str
    node_type: SkillNodeType
    requirements: SkillNodeRequirements
    rewards: Dict[str, Any]  # XP multipliers, special abilities, etc.
    unlock_message: str


# =============================================================================
# REBALANCED SKILL TREE CONFIGURATION
# =============================================================================

# New Progression Structure:
# Level 1: 0 skill points, 0-25 stats (Foundation - Free)
# Level 2: 3 skill points, 50-100 stats (Early Progression)
# Level 3: 8 skill points, 150-250 stats (Intermediate)
# Level 4: 15 skill points, 300-450 stats (Advanced)
# Level 5: 25 skill points, 500-750 stats (Mastery)

REBALANCED_SKILL_TREE_CONFIG: Dict[str, List[SkillTreeNode]] = {
    
    # =========================================================================
    # PULL_VERTICAL - Path of Ascension (5 nodes) - REBALANCED
    # =========================================================================
    "PULL_VERTICAL": [
        SkillTreeNode(
            id="pull_vertical_1",
            category_id="PULL_VERTICAL",
            level=1,
            name="Grip of Shadows",
            description="Master the foundational grip strength needed for all pulling movements",
            lore_text="In the realm of shadows, those who cannot hold on are lost forever. Begin your ascension with an unbreakable grip.",
            node_type=SkillNodeType.FOUNDATION,
            requirements=SkillNodeRequirements(
                strength_stat=0,
                endurance_stat=0,
                technique_stat=0,
                strength_skill_points=0,
                endurance_skill_points=0,
                technique_skill_points=0,
                required_nodes=[],
                min_ascendant_level=1
            ),
            rewards={"pull_xp_multiplier": 1.1, "grip_strength_bonus": 5},
            unlock_message="Your grip tightens like iron chains. The path of ascension begins."
        ),
        SkillTreeNode(
            id="pull_vertical_2",
            category_id="PULL_VERTICAL",
            level=2,
            name="Scapular Awakening",
            description="Learn to engage your shoulder blades for proper pulling mechanics",
            lore_text="The shoulders are the gateway to true pulling power. Awaken the dormant strength within.",
            node_type=SkillNodeType.PROGRESSION,
            requirements=SkillNodeRequirements(
                strength_stat=75,
                endurance_stat=25,
                technique_stat=50,
                strength_skill_points=2,
                endurance_skill_points=0,
                technique_skill_points=1,
                required_nodes=["pull_vertical_1"],
                min_ascendant_level=3
            ),
            rewards={"pull_xp_multiplier": 1.15, "scapular_control": True},
            unlock_message="Your shoulder blades dance with newfound awareness. Power flows through proper form."
        ),
        SkillTreeNode(
            id="pull_vertical_3",
            category_id="PULL_VERTICAL",
            level=3,
            name="Negative Mastery",
            description="Control the descent to build eccentric strength and perfect form",
            lore_text="In the controlled fall lies the secret to rising higher. Master the descent to command the ascent.",
            node_type=SkillNodeType.PROGRESSION,
            requirements=SkillNodeRequirements(
                strength_stat=200,
                endurance_stat=100,
                technique_stat=150,
                strength_skill_points=5,
                endurance_skill_points=1,
                technique_skill_points=2,
                required_nodes=["pull_vertical_2"],
                min_ascendant_level=6
            ),
            rewards={"pull_xp_multiplier": 1.2, "eccentric_strength_bonus": 10},
            unlock_message="You command both rise and fall. The negative becomes your ally."
        ),
        SkillTreeNode(
            id="pull_vertical_4",
            category_id="PULL_VERTICAL",
            level=4,
            name="Ascendant's Rise",
            description="Achieve your first unassisted pull-up through pure strength",
            lore_text="The moment of truth arrives. Rise above gravity through will and strength alone.",
            node_type=SkillNodeType.PROGRESSION,
            requirements=SkillNodeRequirements(
                strength_stat=375,
                endurance_stat=200,
                technique_stat=300,
                strength_skill_points=10,
                endurance_skill_points=3,
                technique_skill_points=2,
                required_nodes=["pull_vertical_3"],
                min_ascendant_level=10
            ),
            rewards={"pull_xp_multiplier": 1.3, "unassisted_pullup": True, "strength_milestone": 5},
            unlock_message="Gravity bows to your will. You rise as a true ascendant."
        ),
        SkillTreeNode(
            id="pull_vertical_5",
            category_id="PULL_VERTICAL",
            level=5,
            name="Master of Ascension",
            description="Transcend basic pulling to achieve multiple consecutive pull-ups",
            lore_text="You have become one with the vertical realm. The sky is no longer a limit, but a playground.",
            node_type=SkillNodeType.MASTERY,
            requirements=SkillNodeRequirements(
                strength_stat=600,
                endurance_stat=350,
                technique_stat=500,
                strength_skill_points=20,
                endurance_skill_points=3,
                technique_skill_points=2,
                required_nodes=["pull_vertical_4"],
                min_ascendant_level=15
            ),
            rewards={"pull_xp_multiplier": 1.5, "master_puller": True, "unlock_weighted_progressions": True},
            unlock_message="You have mastered the art of ascension. The vertical realm bends to your will."
        )
    ],
    
    # =========================================================================
    # UPPER_DYNAMIC - Power Surge (5 nodes) - REBALANCED
    # =========================================================================
    "UPPER_DYNAMIC": [
        SkillTreeNode(
            id="upper_dynamic_1",
            category_id="UPPER_DYNAMIC",
            level=1,
            name="Power Awakening",
            description="Discover the explosive potential within your upper body",
            lore_text="Power lies dormant in every muscle fiber, waiting for the spark of dynamic movement to ignite it.",
            node_type=SkillNodeType.FOUNDATION,
            requirements=SkillNodeRequirements(
                strength_stat=0,
                endurance_stat=0,
                technique_stat=0,
                strength_skill_points=0,
                endurance_skill_points=0,
                technique_skill_points=0,
                required_nodes=[],
                min_ascendant_level=1
            ),
            rewards={"str_points": 1, "xp": 50},
            unlock_message="You have awakened your power! Dynamic energy courses through your upper body."
        ),
        SkillTreeNode(
            id="upper_dynamic_2",
            category_id="UPPER_DYNAMIC",
            level=2,
            name="Surge Initiate",
            description="Learn to channel power through explosive pushing movements",
            lore_text="The initiate learns that true power is not brute force, but the perfect timing of explosive release.",
            node_type=SkillNodeType.PROGRESSION,
            requirements=SkillNodeRequirements(
                strength_stat=100,
                endurance_stat=50,
                technique_stat=75,
                strength_skill_points=2,
                endurance_skill_points=0,
                technique_skill_points=1,
                required_nodes=["upper_dynamic_1"],
                min_ascendant_level=4
            ),
            rewards={"str_points": 2, "xp": 75},
            unlock_message="You have become a Surge Initiate. Explosive power flows through your movements."
        ),
        SkillTreeNode(
            id="upper_dynamic_3",
            category_id="UPPER_DYNAMIC",
            level=3,
            name="Thunder Striker",
            description="Master intermediate explosive movements and power development",
            lore_text="Like thunder follows lightning, the striker's power reverberates through every fiber of their being.",
            node_type=SkillNodeType.PROGRESSION,
            requirements=SkillNodeRequirements(
                strength_stat=250,
                endurance_stat=150,
                technique_stat=200,
                strength_skill_points=6,
                endurance_skill_points=1,
                technique_skill_points=1,
                required_nodes=["upper_dynamic_2"],
                min_ascendant_level=7
            ),
            rewards={"str_points": 3, "end_points": 1, "xp": 100},
            unlock_message="You are now a Thunder Striker. Your power echoes through the realm of strength."
        ),
        SkillTreeNode(
            id="upper_dynamic_4",
            category_id="UPPER_DYNAMIC",
            level=4,
            name="Storm Bringer",
            description="Achieve advanced explosive power and complex dynamic patterns",
            lore_text="The storm bringer commands not just power, but the very tempest of dynamic movement itself.",
            node_type=SkillNodeType.PROGRESSION,
            requirements=SkillNodeRequirements(
                strength_stat=450,
                endurance_stat=300,
                technique_stat=375,
                strength_skill_points=12,
                endurance_skill_points=2,
                technique_skill_points=1,
                required_nodes=["upper_dynamic_3"],
                min_ascendant_level=10
            ),
            rewards={"str_points": 4, "end_points": 2, "xp": 125},
            unlock_message="You have become a Storm Bringer. Dynamic power bends to your will."
        ),
        SkillTreeNode(
            id="upper_dynamic_5",
            category_id="UPPER_DYNAMIC",
            level=5,
            name="Power Incarnate",
            description="Transcend to the highest levels of explosive upper body mastery",
            lore_text="Power Incarnate is not merely strong - they are the living embodiment of dynamic force itself.",
            node_type=SkillNodeType.MASTERY,
            requirements=SkillNodeRequirements(
                strength_stat=750,
                endurance_stat=500,
                technique_stat=600,
                strength_skill_points=20,
                endurance_skill_points=3,
                technique_skill_points=2,
                required_nodes=["upper_dynamic_4"],
                min_ascendant_level=13
            ),
            rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
            unlock_message="You have become Power Incarnate. You are the living essence of explosive strength."
        )
    ],
    
    # =========================================================================
    # MOBILITY_FLOW - Fluid Grace (5 nodes) - REBALANCED
    # =========================================================================
    "MOBILITY_FLOW": [
        SkillTreeNode(
            id="mobility_flow_1",
            category_id="MOBILITY_FLOW",
            level=1,
            name="Flow Awakening",
            description="Begin your journey into the art of fluid movement and mobility",
            lore_text="True strength flows like water - adaptable, persistent, and finding its way through any obstacle.",
            node_type=SkillNodeType.FOUNDATION,
            requirements=SkillNodeRequirements(
                strength_stat=0,
                endurance_stat=0,
                technique_stat=0,
                strength_skill_points=0,
                endurance_skill_points=0,
                technique_skill_points=0,
                required_nodes=[],
                min_ascendant_level=1
            ),
            rewards={"tech_points": 1, "xp": 50},
            unlock_message="You have awakened to the Flow! Movement becomes fluid and graceful."
        ),
        SkillTreeNode(
            id="mobility_flow_2",
            category_id="MOBILITY_FLOW",
            level=2,
            name="Stream Walker",
            description="Develop basic flow patterns and movement transitions",
            lore_text="The stream walker learns that every movement is connected, every transition a bridge to greater mastery.",
            node_type=SkillNodeType.PROGRESSION,
            requirements=SkillNodeRequirements(
                strength_stat=25,
                endurance_stat=50,
                technique_stat=100,
                strength_skill_points=0,
                endurance_skill_points=1,
                technique_skill_points=2,
                required_nodes=["mobility_flow_1"],
                min_ascendant_level=3
            ),
            rewards={"tech_points": 2, "xp": 75},
            unlock_message="You have become a Stream Walker. Your movements flow with natural grace."
        ),
        SkillTreeNode(
            id="mobility_flow_3",
            category_id="MOBILITY_FLOW",
            level=3,
            name="River Dancer",
            description="Master intermediate flow sequences and complex transitions",
            lore_text="The river dancer moves with the rhythm of flowing water, never fighting the current but becoming one with it.",
            node_type=SkillNodeType.PROGRESSION,
            requirements=SkillNodeRequirements(
                strength_stat=100,
                endurance_stat=150,
                technique_stat=250,
                strength_skill_points=1,
                endurance_skill_points=2,
                technique_skill_points=5,
                required_nodes=["mobility_flow_2"],
                min_ascendant_level=6
            ),
            rewards={"tech_points": 3, "end_points": 1, "xp": 100},
            unlock_message="You have become a River Dancer. Flow and grace define your every movement."
        ),
        SkillTreeNode(
            id="mobility_flow_4",
            category_id="MOBILITY_FLOW",
            level=4,
            name="Torrent Master",
            description="Achieve advanced flow states and complex movement patterns",
            lore_text="The torrent master commands the full spectrum of movement, from gentle streams to raging rapids.",
            node_type=SkillNodeType.PROGRESSION,
            requirements=SkillNodeRequirements(
                strength_stat=200,
                endurance_stat=350,
                technique_stat=450,
                strength_skill_points=2,
                endurance_skill_points=3,
                technique_skill_points=10,
                required_nodes=["mobility_flow_3"],
                min_ascendant_level=9
            ),
            rewards={"tech_points": 4, "end_points": 2, "str_points": 1, "xp": 125},
            unlock_message="You have become a Torrent Master. Movement flows through you like a force of nature."
        ),
        SkillTreeNode(
            id="mobility_flow_5",
            category_id="MOBILITY_FLOW",
            level=5,
            name="Flow Incarnate",
            description="Transcend physical limitations through perfect movement harmony",
            lore_text="Flow Incarnate moves beyond technique into pure artistry, where every gesture is poetry in motion.",
            node_type=SkillNodeType.MASTERY,
            requirements=SkillNodeRequirements(
                strength_stat=350,
                endurance_stat=600,
                technique_stat=750,
                strength_skill_points=3,
                endurance_skill_points=5,
                technique_skill_points=17,
                required_nodes=["mobility_flow_4"],
                min_ascendant_level=12
            ),
            rewards={"tech_points": 6, "end_points": 4, "str_points": 2, "xp": 200},
            unlock_message="You have become Flow Incarnate. You are movement itself, pure and transcendent."
        )
    ]
}

# =============================================================================
# PROGRESSION VALIDATION AND HELPER FUNCTIONS
# =============================================================================

def validate_rebalanced_progression():
    """Validate that the rebalanced skill tree maintains proper progression"""
    for category, nodes in REBALANCED_SKILL_TREE_CONFIG.items():
        print(f"\n{category} Progression Analysis:")
        total_skill_points = 0
        
        for node in nodes:
            req = node.requirements
            skill_cost = req.strength_skill_points + req.endurance_skill_points + req.technique_skill_points
            total_skill_points += skill_cost
            
            print(f"  Level {node.level}: {skill_cost} skill points, "
                  f"Stats: STR={req.strength_stat}, END={req.endurance_stat}, TECH={req.technique_stat}")
        
        print(f"  Total skill points to max: {total_skill_points}")
        print(f"  Stat points needed: {total_skill_points * 150}")

if __name__ == "__main__":
    validate_rebalanced_progression()