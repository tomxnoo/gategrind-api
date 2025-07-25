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
# SKILL TREE CONFIGURATION
# =========================================================================

SKILL_TREE_CONFIG: Dict[str, List[SkillTreeNode]] = {}

# =========================================================================
# UPPER_DYNAMIC - Power Surge (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["UPPER_DYNAMIC"] = [
    SkillTreeNode(
        id="upper_dynamic_1",
        category_id="UPPER_DYNAMIC",
        level=1,
        name="Power Awakening",
        description="Discover the explosive potential within your upper body",
        lore_text="Power lies dormant in every muscle fiber, waiting for the spark of dynamic movement to ignite it.",
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
        unlock_message="You have become Power Incarnate. You are the living essence of explosive strength."
    )
]

# =========================================================================
# MOBILITY_FLOW - Fluid Grace (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["MOBILITY_FLOW"] = [
    SkillTreeNode(
        id="mobility_flow_1",
        category_id="MOBILITY_FLOW",
        level=1,
        name="Flow Awakening",
        description="Begin your journey into the art of fluid movement and mobility",
        lore_text="True strength flows like water - adaptable, persistent, and finding its way through any obstacle.",
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
            str_points=250,
            end_points=500,
            tech_points=500,
            skill_points=3,
            strength_skill_points=0,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["mobility_flow_1"],
            min_ascendant_level=3
        ),
        rewards={"tech_points": 2, "xp": 75},
        unlock_message="You have become a Stream Walker. Your movements flow with natural grace."
    ),
    SkillTreeNode(
        id="mobility_flow_3",
        category_id="MOBILITY_FLOW",
        level=3,
        name="Current Rider",
        description="Master intermediate flow states and complex movement patterns",
        lore_text="The current rider moves with the rhythm of the universe, finding harmony in motion.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=1000,
            tech_points=1000,
            skill_points=8,
            strength_skill_points=1,
            endurance_skill_points=3,
            technique_skill_points=4,
            prerequisite_nodes=["mobility_flow_2"],
            min_ascendant_level=6
        ),
        rewards={"tech_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You are now a Current Rider. You move in perfect harmony with the flow of movement."
    ),
    SkillTreeNode(
        id="mobility_flow_4",
        category_id="MOBILITY_FLOW",
        level=4,
        name="Torrent Master",
        description="Achieve advanced flow mastery and dynamic movement control",
        lore_text="The torrent master commands the very essence of movement, bending flow to their will.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=750,
            end_points=1500,
            tech_points=1500,
            skill_points=15,
            strength_skill_points=2,
            endurance_skill_points=5,
            technique_skill_points=8,
            prerequisite_nodes=["mobility_flow_3"],
            min_ascendant_level=9
        ),
        rewards={"tech_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have become a Torrent Master. Flow and movement bend to your mastery."
    ),
    SkillTreeNode(
        id="mobility_flow_5",
        category_id="MOBILITY_FLOW",
        level=5,
        name="Flow Incarnate",
        description="Transcend to become one with the eternal flow of movement",
        lore_text="Flow Incarnate is movement itself - the living embodiment of fluid grace and perfect mobility.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=2000,
            tech_points=2000,
            skill_points=25,
            strength_skill_points=3,
            endurance_skill_points=8,
            technique_skill_points=14,
            prerequisite_nodes=["mobility_flow_4"],
            min_ascendant_level=12
        ),
        rewards={"tech_points": 6, "end_points": 3, "str_points": 2, "xp": 200},
        unlock_message="You have become Flow Incarnate. You are the living essence of perfect movement."
    )
]

# =========================================================================
# PULL_VERTICAL - Ascending Force (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["PULL_VERTICAL"] = [
    SkillTreeNode(
        id="pull_vertical_1",
        category_id="PULL_VERTICAL",
        level=1,
        name="Grip Awakening",
        description="Discover the foundational power of vertical pulling movements",
        lore_text="Every great ascent begins with a single grip, a moment where earth meets sky through will alone.",
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
        unlock_message="You have awakened your grip! The power to ascend flows through your hands."
    ),
    SkillTreeNode(
        id="pull_vertical_2",
        category_id="PULL_VERTICAL",
        level=2,
        name="Ascent Seeker",
        description="Develop fundamental vertical pulling strength and technique",
        lore_text="The seeker looks upward, knowing that every pull brings them closer to their highest potential.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=1,
            technique_skill_points=0,
            prerequisite_nodes=["pull_vertical_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have become an Ascent Seeker. Your pull grows stronger with each movement."
    ),
    SkillTreeNode(
        id="pull_vertical_3",
        category_id="PULL_VERTICAL",
        level=3,
        name="Sky Reacher",
        description="Master intermediate pulling patterns and grip strength",
        lore_text="The sky reacher knows no ceiling, for their strength extends beyond the limits of earth.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=2,
            technique_skill_points=1,
            prerequisite_nodes=["pull_vertical_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "tech_points": 1, "xp": 100},
        unlock_message="You are now a Sky Reacher. Your pull defies the very pull of gravity."
    ),
    SkillTreeNode(
        id="pull_vertical_4",
        category_id="PULL_VERTICAL",
        level=4,
        name="Heaven Climber",
        description="Achieve advanced vertical pulling mastery and complex movements",
        lore_text="The heaven climber ascends not just in body, but in spirit, reaching toward divine strength.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=3,
            technique_skill_points=2,
            prerequisite_nodes=["pull_vertical_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "tech_points": 2, "xp": 125},
        unlock_message="You have become a Heaven Climber. Your ascent knows no bounds."
    ),
    SkillTreeNode(
        id="pull_vertical_5",
        category_id="PULL_VERTICAL",
        level=5,
        name="Ascension Master",
        description="Transcend to the ultimate mastery of vertical pulling force",
        lore_text="Ascension Master has conquered gravity itself, becoming one with the eternal upward force.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=4,
            technique_skill_points=3,
            prerequisite_nodes=["pull_vertical_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "tech_points": 3, "end_points": 2, "xp": 200},
        unlock_message="You have become an Ascension Master. You are the living embodiment of upward force."
    )
]


# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

def get_skill_tree_categories() -> List[str]:
    """Get all available skill tree categories"""
    return list(SKILL_TREE_CONFIG.keys())


def get_category_nodes(category_id: str) -> List[SkillTreeNode]:
    """Get all nodes for a specific category"""
    return SKILL_TREE_CONFIG.get(category_id, [])


def get_node_by_id(node_id: str) -> Optional[SkillTreeNode]:
    """Get a specific node by its ID"""
    for category_nodes in SKILL_TREE_CONFIG.values():
        for node in category_nodes:
            if node.id == node_id:
                return node
    return None


def calculate_total_category_cost(category_id: str) -> Dict[str, int]:
    """Calculate total skill point cost to max out a category"""
    nodes = get_category_nodes(category_id)
    total_cost = {
        "skill_points": 0,
        "strength_skill_points": 0,
        "endurance_skill_points": 0,
        "technique_skill_points": 0
    }
    
    for node in nodes:
        req = node.requirements
        total_cost["skill_points"] += req.skill_points
        total_cost["strength_skill_points"] += req.strength_skill_points
        total_cost["endurance_skill_points"] += req.endurance_skill_points
        total_cost["technique_skill_points"] += req.technique_skill_points
    
    return total_cost


def validate_skill_tree_config() -> bool:
    """Validate the skill tree configuration for consistency"""
    for category_id, nodes in SKILL_TREE_CONFIG.items():
        # Check that we have exactly 5 levels
        if len(nodes) != 5:
            print(f"ERROR: Category {category_id} has {len(nodes)} nodes, expected 5")
            return False
        
        # Check level progression
        for i, node in enumerate(nodes, 1):
            if node.level != i:
                print(f"ERROR: Node {node.id} has level {node.level}, expected {i}")
                return False
        
        # Check prerequisite chains
        for i, node in enumerate(nodes):
            if i == 0:  # First node should have no prerequisites
                if node.requirements.prerequisite_nodes:
                    print(f"ERROR: First node {node.id} has prerequisites")
                    return False
            else:  # Other nodes should require previous node
                expected_prereq = nodes[i-1].id
                if expected_prereq not in node.requirements.prerequisite_nodes:
                    print(f"ERROR: Node {node.id} missing prerequisite {expected_prereq}")
                    return False
    
    return True


# Validate configuration on import
if __name__ == "__main__":
    if validate_skill_tree_config():
        print("✅ Skill tree configuration is valid!")
        
        # Print summary
        for category_id in get_skill_tree_categories():
            cost = calculate_total_category_cost(category_id)
            print(f"\n{category_id} total cost:")
            for cost_type, amount in cost.items():
                if amount > 0:
                    print(f"  {cost_type}: {amount}")
    else:
        print("❌ Skill tree configuration has errors!")