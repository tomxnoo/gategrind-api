#!/usr/bin/env python3
"""
Create Missing Skill Tree Nodes Script

This script creates all the missing skill tree nodes based on the 
COMPLETE_MOVEMENTS_SOURCE_OF_TRUTH.md document.

Usage: python create_missing_skill_nodes.py
"""

import asyncio
import sys
from typing import Dict, List, Any
from datetime import datetime, timezone

sys.path.append('/home/runner/workspace')

from app.infrastructure.database.session import get_async_session
from app.infrastructure.database.models.v2 import SkillTreeNode, MovementCategory
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

class SkillNodeCreator:
    def __init__(self):
        self.nodes_created = 0
        self.nodes_skipped = 0
        self.errors = []

    async def create_all_missing_nodes(self):
        """Create all missing skill tree nodes."""
        print("🌳 Creating missing skill tree nodes...")
        
        async for session in get_async_session():
            try:
                # Get existing nodes to avoid duplicates
                existing_nodes = await self.get_existing_nodes(session)
                print(f"📋 Found {len(existing_nodes)} existing nodes")
                
                # Get all categories to validate they exist
                categories = await self.get_all_categories(session)
                category_ids = {cat.category_id for cat in categories}
                print(f"📋 Found {len(category_ids)} categories: {sorted(category_ids)}")
                
                # Define all skill nodes that should exist based on source of truth
                nodes_to_create = self.get_skill_nodes_definition()
                
                for node_data in nodes_to_create:
                    category_id = node_data["category_id"]
                    node_id = node_data["node_id"]
                    
                    # Check if category exists
                    if category_id not in category_ids:
                        print(f"⚠️  Category {category_id} doesn't exist, skipping {node_id}")
                        self.nodes_skipped += 1
                        continue
                    
                    # Check if node already exists
                    if node_id in existing_nodes:
                        print(f"✅ Node {node_id} already exists, skipping")
                        self.nodes_skipped += 1
                        continue
                    
                    # Create the node
                    try:
                        await self.create_skill_node(session, node_data)
                        self.nodes_created += 1
                        print(f"✨ Created node: {node_id} ({node_data['name']})")
                    except Exception as e:
                        error_msg = f"Failed to create {node_id}: {e}"
                        self.errors.append(error_msg)
                        print(f"❌ {error_msg}")
                
                # Commit all changes
                await session.commit()
                print(f"\n🎉 Node creation complete!")
                print(f"   Created: {self.nodes_created}")
                print(f"   Skipped: {self.nodes_skipped}")
                print(f"   Errors: {len(self.errors)}")
                
                if self.errors:
                    print(f"\n❌ Errors encountered:")
                    for error in self.errors:
                        print(f"   - {error}")
                
                break
                
            except Exception as e:
                print(f"❌ Error during node creation: {e}")
                await session.rollback()
                raise

    async def get_existing_nodes(self, session: AsyncSession) -> set:
        """Get all existing node IDs."""
        result = await session.execute(text("SELECT node_id FROM skill_tree_nodes;"))
        return {row[0] for row in result.fetchall()}

    async def get_all_categories(self, session: AsyncSession):
        """Get all movement categories."""
        result = await session.execute(select(MovementCategory))
        return result.scalars().all()

    async def create_skill_node(self, session: AsyncSession, node_data: Dict[str, Any]):
        """Create a single skill tree node."""
        node = SkillTreeNode(
            node_id=node_data["node_id"],
            category_id=node_data["category_id"],
            level=node_data["level"],
            name=node_data["name"],
            description=node_data["description"],
            required_ascendant_level=node_data["required_ascendant_level"],
            required_str_points=node_data["required_str_points"],
            required_end_points=node_data["required_end_points"],
            required_tech_points=node_data["required_tech_points"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        session.add(node)
        await session.flush()  # Flush to get the ID

    def get_skill_nodes_definition(self) -> List[Dict[str, Any]]:
        """Define all skill nodes that should exist based on the source of truth."""
        nodes = []
        
        # PULL_UNILATERAL progression (the one that was failing)
        nodes.extend([
            {
                "node_id": "pull_unilateral_1",
                "category_id": "PULL_UNILATERAL", 
                "level": 1,
                "name": "Unilateral Pulling - Foundation",
                "description": "Master the basics of single-arm pulling movements",
                "required_ascendant_level": 1,
                "required_str_points": 0,
                "required_end_points": 0,
                "required_tech_points": 0
            },
            {
                "node_id": "pull_unilateral_2",
                "category_id": "PULL_UNILATERAL",
                "level": 2, 
                "name": "Unilateral Pulling - First Ascent",
                "description": "Develop single-arm pulling strength and control",
                "required_ascendant_level": 3,
                "required_str_points": 500,
                "required_end_points": 250,
                "required_tech_points": 250
            },
            {
                "node_id": "pull_unilateral_3",
                "category_id": "PULL_UNILATERAL",
                "level": 3,
                "name": "Unilateral Pulling - Competence", 
                "description": "Achieve competence in advanced single-arm techniques",
                "required_ascendant_level": 6,
                "required_str_points": 1000,
                "required_end_points": 500,
                "required_tech_points": 500
            },
            {
                "node_id": "pull_unilateral_4",
                "category_id": "PULL_UNILATERAL",
                "level": 4,
                "name": "Unilateral Pulling - Strength",
                "description": "Master high-level single-arm pulling movements",
                "required_ascendant_level": 10,
                "required_str_points": 1500,
                "required_end_points": 750,
                "required_tech_points": 750
            },
            {
                "node_id": "pull_unilateral_5", 
                "category_id": "PULL_UNILATERAL",
                "level": 5,
                "name": "Unilateral Pulling - Mastery",
                "description": "Achieve ultimate mastery of one-arm pull-ups and beyond",
                "required_ascendant_level": 15,
                "required_str_points": 2000,
                "required_end_points": 1000,
                "required_tech_points": 1000
            }
        ])
        
        # PULL_VERTICAL progression
        nodes.extend([
            {
                "node_id": "pull_vertical_1",
                "category_id": "PULL_VERTICAL",
                "level": 1,
                "name": "Grip of Shadows",
                "description": "Begin your ascension with the fundamental grip",
                "required_ascendant_level": 1,
                "required_str_points": 0,
                "required_end_points": 0,
                "required_tech_points": 0
            },
            {
                "node_id": "pull_vertical_2",
                "category_id": "PULL_VERTICAL",
                "level": 2,
                "name": "Scapular Awakening", 
                "description": "Awaken the power within your shoulder blades",
                "required_ascendant_level": 3,
                "required_str_points": 75,
                "required_end_points": 25,
                "required_tech_points": 50
            },
            {
                "node_id": "pull_vertical_3",
                "category_id": "PULL_VERTICAL",
                "level": 3,
                "name": "Negative Mastery",
                "description": "Control the descent, master the ascent",
                "required_ascendant_level": 6,
                "required_str_points": 200,
                "required_end_points": 100,
                "required_tech_points": 150
            },
            {
                "node_id": "pull_vertical_4",
                "category_id": "PULL_VERTICAL",
                "level": 4,
                "name": "Ascendant's Rise",
                "description": "Rise above mortal limitations",
                "required_ascendant_level": 10,
                "required_str_points": 375,
                "required_end_points": 200,
                "required_tech_points": 300
            },
            {
                "node_id": "pull_vertical_5",
                "category_id": "PULL_VERTICAL",
                "level": 5,
                "name": "Master of Ascension",
                "description": "Achieve ultimate vertical pulling mastery",
                "required_ascendant_level": 15,
                "required_str_points": 600,
                "required_end_points": 350,
                "required_tech_points": 500
            }
        ])
        
        # UPPER_DYNAMIC progression (already has upper_dynamic_1, add the rest)
        nodes.extend([
            {
                "node_id": "upper_dynamic_2",
                "category_id": "UPPER_DYNAMIC",
                "level": 2,
                "name": "Surge Initiate",
                "description": "Channel explosive upper body power",
                "required_ascendant_level": 4,
                "required_str_points": 500,
                "required_end_points": 250,
                "required_tech_points": 250
            },
            {
                "node_id": "upper_dynamic_3",
                "category_id": "UPPER_DYNAMIC",
                "level": 3,
                "name": "Thunder Striker",
                "description": "Strike with the force of thunder",
                "required_ascendant_level": 7,
                "required_str_points": 1000,
                "required_end_points": 500,
                "required_tech_points": 500
            },
            {
                "node_id": "upper_dynamic_4", 
                "category_id": "UPPER_DYNAMIC",
                "level": 4,
                "name": "Storm Bringer",
                "description": "Bring forth the storm of dynamic power",
                "required_ascendant_level": 10,
                "required_str_points": 1500,
                "required_end_points": 750,
                "required_tech_points": 750
            },
            {
                "node_id": "upper_dynamic_5",
                "category_id": "UPPER_DYNAMIC",
                "level": 5,
                "name": "Power Incarnate",
                "description": "Become the living embodiment of explosive power",
                "required_ascendant_level": 13,
                "required_str_points": 2000,
                "required_end_points": 1000,
                "required_tech_points": 1000
            }
        ])
        
        # MOBILITY_FLOW progression
        nodes.extend([
            {
                "node_id": "mobility_flow_1",
                "category_id": "MOBILITY_FLOW",
                "level": 1,
                "name": "Flow Awakening",
                "description": "Awaken the fluid grace within",
                "required_ascendant_level": 1,
                "required_str_points": 0,
                "required_end_points": 0,
                "required_tech_points": 0
            },
            {
                "node_id": "mobility_flow_2",
                "category_id": "MOBILITY_FLOW",
                "level": 2,
                "name": "Stream Walker",
                "description": "Move like water through the world",
                "required_ascendant_level": 3,
                "required_str_points": 25,
                "required_end_points": 50,
                "required_tech_points": 100
            },
            {
                "node_id": "mobility_flow_3",
                "category_id": "MOBILITY_FLOW",
                "level": 3,
                "name": "River Dancer",
                "description": "Dance with the flowing river of movement",
                "required_ascendant_level": 6,
                "required_str_points": 100,
                "required_end_points": 150,
                "required_tech_points": 250
            },
            {
                "node_id": "mobility_flow_4",
                "category_id": "MOBILITY_FLOW",
                "level": 4,
                "name": "Torrent Master",
                "description": "Master the torrential flow of advanced movement",
                "required_ascendant_level": 9,
                "required_str_points": 200,
                "required_end_points": 350,
                "required_tech_points": 450
            },
            {
                "node_id": "mobility_flow_5",
                "category_id": "MOBILITY_FLOW", 
                "level": 5,
                "name": "Flow Incarnate",
                "description": "Become one with the eternal flow of movement",
                "required_ascendant_level": 12,
                "required_str_points": 350,
                "required_end_points": 600,
                "required_tech_points": 750
            }
        ])
        
        # Add more core categories that are commonly used
        # PUSH_HORIZONTAL progression
        nodes.extend([
            {
                "node_id": "push_horizontal_1",
                "category_id": "PUSH_HORIZONTAL",
                "level": 1,
                "name": "Earthbreaker's Foundation",
                "description": "Ground yourself in horizontal pushing power",
                "required_ascendant_level": 1,
                "required_str_points": 0,
                "required_end_points": 0,
                "required_tech_points": 0
            },
            {
                "node_id": "push_horizontal_2",
                "category_id": "PUSH_HORIZONTAL",
                "level": 2,
                "name": "Earthbreaker's Might",
                "description": "Channel the earth's power through your arms",
                "required_ascendant_level": 3,
                "required_str_points": 500,
                "required_end_points": 250,
                "required_tech_points": 250
            },
            {
                "node_id": "push_horizontal_3",
                "category_id": "PUSH_HORIZONTAL",
                "level": 3,
                "name": "Earthbreaker's Force",
                "description": "Strike with the force of tectonic plates",
                "required_ascendant_level": 6,
                "required_str_points": 1000,
                "required_end_points": 500,
                "required_tech_points": 500
            },
            {
                "node_id": "push_horizontal_4",
                "category_id": "PUSH_HORIZONTAL",
                "level": 4,
                "name": "Earthbreaker's Dominion",
                "description": "Dominate with overwhelming horizontal power",
                "required_ascendant_level": 10,
                "required_str_points": 1500,
                "required_end_points": 750,
                "required_tech_points": 750
            },
            {
                "node_id": "push_horizontal_5",
                "category_id": "PUSH_HORIZONTAL",
                "level": 5,
                "name": "Earthbreaker's Supremacy",
                "description": "Achieve supreme mastery of horizontal pushing",
                "required_ascendant_level": 15,
                "required_str_points": 2000,
                "required_end_points": 1000,
                "required_tech_points": 1000
            }
        ])
        
        return nodes

    def print_summary(self):
        """Print a summary of the operation."""
        total_nodes = len(self.get_skill_nodes_definition())
        print(f"\n📊 Summary:")
        print(f"   Total nodes defined: {total_nodes}")
        print(f"   Nodes created: {self.nodes_created}")
        print(f"   Nodes skipped: {self.nodes_skipped}")
        print(f"   Errors: {len(self.errors)}")

async def main():
    """Main execution function."""
    print("🚀 Starting Missing Skill Tree Node Creation")
    print("=" * 60)
    
    creator = SkillNodeCreator()
    await creator.create_all_missing_nodes()
    creator.print_summary()

if __name__ == "__main__":
    asyncio.run(main())