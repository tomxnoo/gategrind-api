#!/usr/bin/env python3
"""
Fix for skill tree UI categorization.

The current issue is that "Upper Body" button only shows PUSH category
instead of all upper body categories (PUSH, PULL, PULL_VERTICAL, etc.).

This script updates the skill tree panel to properly group categories.
"""

import os

def create_category_groups_mapping():
    """Create the category groups mapping to add to the skill tree panel."""
    
    category_groups_code = '''
# =========================================================================
# CATEGORY GROUPS MAPPING
# =========================================================================

CATEGORY_GROUPS = {
    "upper_body": {
        "name": "💪 Upper Body",
        "description": "Push, pull and overhead movement patterns",
        "categories": [
            "PUSH", "PULL", "PULL_VERTICAL", "UPPER_DYNAMIC", 
            "BALLISTIC", "PLYOMETRIC", "GRIP"
        ]
    },
    "lower_body": {
        "name": "🦵 Lower Body", 
        "description": "Squats, lunges, hinges and locomotion",
        "categories": [
            "SQUAT", "LUNGE", "HINGE", "GAIT", "LOADED_CARRY", 
            "GROUND_MOVEMENT", "AGILITY", "POWER", "SPEED"
        ]
    },
    "core_stability": {
        "name": "🎯 Core & Stability",
        "description": "Core strength, balance and stability",
        "categories": [
            "CORE", "ROTATION", "BALANCE", "COORDINATION", 
            "FLEXIBILITY", "MOBILITY_FLOW", "REACTION"
        ]
    },
    "performance": {
        "name": "⚡ Performance",
        "description": "Strength, endurance and performance attributes", 
        "categories": [
            "STRENGTH", "ENDURANCE", "TECHNIQUE", "TACTICAL",
            "DEFENSIVE", "OFFENSIVE", "COMPETITIVE"
        ]
    },
    "recovery": {
        "name": "🔄 Recovery & Health",
        "description": "Recovery, injury prevention and corrective work",
        "categories": [
            "RECOVERY", "INJURY_PREVENTION", "REHABILITATION", 
            "CORRECTIVE", "MENTAL", "STRATEGIC"
        ]
    },
    "specialized": {
        "name": "🎖️ Specialized",
        "description": "Advanced and sport-specific movements",
        "categories": [
            "FUNCTIONAL", "SPORT_SPECIFIC", "ADVANCED"
        ]
    }
}

def get_categories_for_group(group_id: str) -> List[str]:
    """Get list of category IDs for a given group."""
    return CATEGORY_GROUPS.get(group_id, {}).get("categories", [])

def get_group_info(group_id: str) -> Dict[str, Any]:
    """Get group information including name, description, and categories."""
    return CATEGORY_GROUPS.get(group_id, {})
'''
    
    return category_groups_code

def create_updated_embed_function():
    """Create the updated embed function that handles multiple categories."""
    
    embed_function_code = '''async def build_skill_tree_embed(bot: discord.Client, user: Union[discord.User, discord.Member], category: Optional[str] = None, category_group: Optional[str] = None) -> discord.Embed:
    """
    Build the skill tree panel embed showing movement library data.
    
    Args:
        bot: The Discord bot instance
        user: The Discord user to show the panel for
        category: Optional single category ID to show specific category details
        category_group: Optional category group to show multiple related categories
        
    Returns:
        discord.Embed: The formatted embed for display
    """
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("skill_tree")

    try:
        # Use cached data to improve performance
        library_data = await get_cached_library_data(user)
        
        if not library_data or 'categories' not in library_data:
            embed = discord.Embed(
                title="Skill Tree - Error",
                description="❌ Unable to load skill tree data. Please try again.",
                color=0xFF0000
            )
            embed.add_field(name="Status", value=header, inline=False)
            return embed

        # Get profile data for unlocked skills
        try:
            profile_data = await get_cached_profile_data(user)
            unlocked_skill_ids = set(skill.get('id') for skill in profile_data.get('unlocked_skills', []))
            user_stats = profile_data.get('stats', {})
        except:
            unlocked_skill_ids = set()
            user_stats = {}

        categories_data = library_data['categories']
        
        # Handle category group display
        if category_group:
            group_info = get_group_info(category_group)
            if not group_info:
                embed = discord.Embed(
                    title="Skill Tree - Error", 
                    description=f"❌ Unknown category group: {category_group}",
                    color=0xFF0000
                )
                embed.add_field(name="Status", value=header, inline=False)
                return embed
                
            # Filter categories to show only those in the group
            target_category_ids = group_info["categories"]
            filtered_categories = [cat for cat in categories_data if cat.get('id') in target_category_ids]
            
            embed = discord.Embed(
                title=f"Skill Tree - {group_info['name']}",
                description=f"{sub_header}\\n\\n{group_info['description']}",
                color=0x4A90E2
            )
            
            # Show summary stats for the group
            total_nodes = sum(len(cat.get('skill_nodes', [])) for cat in filtered_categories)
            unlocked_in_group = sum(
                1 for cat in filtered_categories 
                for node in cat.get('skill_nodes', []) 
                if node.get('id') in unlocked_skill_ids
            )
            
            embed.add_field(
                name="📊 Group Progress",
                value=f"**Unlocked:** {unlocked_in_group}/{total_nodes} skills\\n**Categories:** {len(filtered_categories)} available",
                inline=True
            )
            
            # Add category details
            for cat in filtered_categories[:6]:  # Limit to prevent embed size issues
                cat_nodes = cat.get('skill_nodes', [])
                unlocked_count = sum(1 for node in cat_nodes if node.get('id') in unlocked_skill_ids)
                
                # Get next unlockable skill
                next_skill = None
                for node in cat_nodes:
                    if node.get('id') not in unlocked_skill_ids:
                        next_skill = node
                        break
                
                progress_bar = create_progress_bar(unlocked_count, len(cat_nodes), 10)
                next_info = f"\\n🎯 Next: **{next_skill.get('name', 'N/A')}**" if next_skill else "\\n✅ **Complete**"
                
                embed.add_field(
                    name=f"{cat.get('display_name', cat.get('name', 'Unknown'))}",
                    value=f"{progress_bar} ({unlocked_count}/{len(cat_nodes)}){next_info}",
                    inline=True
                )
            
            if len(filtered_categories) > 6:
                embed.add_field(
                    name="Additional Categories",
                    value=f"... and {len(filtered_categories) - 6} more categories",
                    inline=False
                )
                
        # Handle single category display (existing logic)
        elif category:
            cat_data = next((cat for cat in categories_data if cat.get('id') == category), None)
            if not cat_data:
                embed = discord.Embed(
                    title="Skill Tree - Error",
                    description=f"❌ Category '{category}' not found.",
                    color=0xFF0000
                )
                embed.add_field(name="Status", value=header, inline=False)
                return embed

            skill_nodes = cat_data.get('skill_nodes', [])
            
            embed = discord.Embed(
                title=f"Skill Tree - {cat_data.get('display_name', cat_data.get('name', 'Unknown'))}",
                description=f"{sub_header}\\n\\n{cat_data.get('description', 'No description available.')}",
                color=0x4A90E2
            )

            # Show skill progression for this category
            unlocked_count = sum(1 for node in skill_nodes if node.get('id') in unlocked_skill_ids)
            progress_bar = create_progress_bar(unlocked_count, len(skill_nodes), 15)
            
            embed.add_field(
                name="📊 Category Progress", 
                value=f"{progress_bar}\\n**Unlocked:** {unlocked_count}/{len(skill_nodes)} skills",
                inline=False
            )

            # Show skill details
            for i, node in enumerate(skill_nodes[:8]):  # Limit to 8 skills
                node_id = node.get('id')
                is_unlocked = node_id in unlocked_skill_ids
                
                status_emoji = "✅" if is_unlocked else "🔒"
                level_info = f"Level {node.get('level', '?')}"
                
                embed.add_field(
                    name=f"{status_emoji} {node.get('name', 'Unknown')}",
                    value=f"**{level_info}**\\n{node.get('description', 'No description')}",
                    inline=True
                )
            
            if len(skill_nodes) > 8:
                embed.add_field(
                    name="Additional Skills",
                    value=f"... and {len(skill_nodes) - 8} more skills",
                    inline=False
                )
        
        # Handle overview display (existing logic)
        else:
            embed = discord.Embed(
                title="🌟 Skill Tree Overview",
                description=f"{sub_header}\\n\\nExplore movement categories to unlock and master new skills.",
                color=0x4A90E2
            )

            # Calculate overview stats
            total_skills = sum(len(cat.get('skill_nodes', [])) for cat in categories_data)
            total_unlocked = len(unlocked_skill_ids)
            
            embed.add_field(
                name="📊 Overall Progress",
                value=f"**Total Unlocked:** {total_unlocked}/{total_skills} skills\\n**Categories:** {len(categories_data)} available",
                inline=False
            )

            # Show category groups
            for group_id, group_info in CATEGORY_GROUPS.items():
                group_categories = [cat for cat in categories_data if cat.get('id') in group_info["categories"]]
                group_total = sum(len(cat.get('skill_nodes', [])) for cat in group_categories)
                group_unlocked = sum(
                    1 for cat in group_categories 
                    for node in cat.get('skill_nodes', []) 
                    if node.get('id') in unlocked_skill_ids
                )
                
                progress_bar = create_progress_bar(group_unlocked, group_total, 10)
                
                embed.add_field(
                    name=group_info["name"],
                    value=f"{progress_bar}\\n{group_unlocked}/{group_total} skills\\n*{group_info['description']}*",
                    inline=True
                )

        embed.add_field(name="Status", value=header, inline=False)
        return embed

    except Exception as e:
        logger.error(f"Error building skill tree embed: {e}")
        embed = discord.Embed(
            title="Skill Tree - Error",
            description="❌ An error occurred while loading the skill tree. Please try again.",
            color=0xFF0000
        )
        embed.add_field(name="Status", value=header, inline=False)
        return embed'''
    
    return embed_function_code

def create_updated_button_callbacks():
    """Create updated button callback functions."""
    
    button_callbacks = '''    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        
        async def do_work():
            # Show upper body category group instead of single category
            embed = await build_skill_tree_embed(self.bot, self.user, category_group="upper_body")
            view = SkillTreeView(self.bot, self.user)
            view.current_category_group = "upper_body"
            
            # Check if there are unlockable skills in upper body categories
            library_data = await get_cached_library_data(self.user)
            has_unlockable = await check_has_unlockable_skills_in_group(self.user, "upper_body", library_data)
            view.update_unlock_button("upper_body", has_unlockable, is_group=True)
            
            return embed, view

        await run_with_animation(interaction, do_work)'''
    
    return button_callbacks

def update_skill_tree_panel():
    """Update the skill tree panel with category groups support."""
    
    panel_path = os.path.join(os.getcwd(), "features/skills/ui/skill_tree_panel.py")
    
    if not os.path.exists(panel_path):
        print(f"❌ Could not find skill_tree_panel.py at {panel_path}")
        return False
    
    print("📖 Reading skill_tree_panel.py...")
    
    with open(panel_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add category groups mapping after imports
    import_end = content.find('logger = logging.getLogger(__name__)')
    if import_end == -1:
        print("❌ Could not find logger definition")
        return False
    
    import_end = content.find('\n', import_end) + 1
    
    # Insert category groups mapping
    category_groups_code = create_category_groups_mapping()
    new_content = content[:import_end] + '\n' + category_groups_code + '\n' + content[import_end:]
    
    # Update build_skill_tree_embed function signature and logic
    # Find the function definition
    func_start = new_content.find('async def build_skill_tree_embed(')
    if func_start == -1:
        print("❌ Could not find build_skill_tree_embed function")
        return False
    
    # Find the end of the function (next async def or class)
    func_end = new_content.find('\nasync def ', func_start + 1)
    if func_end == -1:
        func_end = new_content.find('\nclass ', func_start + 1)
    if func_end == -1:
        func_end = len(new_content)
    
    # Replace the function
    updated_embed_function = create_updated_embed_function()
    new_content = new_content[:func_start] + updated_embed_function + new_content[func_end:]
    
    print("✏️ Writing updated skill_tree_panel.py...")
    
    with open(panel_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Successfully updated skill tree panel with category groups!")
    print("\nNext steps:")
    print("1. The UI will now show category groups (Upper Body, Lower Body, etc.)")
    print("2. Each group will display multiple related categories")
    print("3. Users can see progress across entire groups")
    
    return True

if __name__ == "__main__":
    print("=" * 80)
    print("SKILL TREE CATEGORIZATION FIX")
    print("=" * 80)
    print("This script fixes the skill tree UI to show category groups")
    print("instead of single categories for Upper Body, Lower Body, etc.")
    print()
    
    try:
        success = update_skill_tree_panel()
        if success:
            print("\n🎉 Categorization fix completed successfully!")
        else:
            print("\n❌ Fix failed - check output above")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()