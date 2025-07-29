#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from features.skills.ui.skill_tree_panel import (
    normalize_category_id, 
    get_category_group_mapping, 
    find_categories_for_group,
    get_category_position_info,
    get_cached_library_data
)
from core.api.api_client import APIClient

# Mock user class for testing
class MockUser:
    def __init__(self, user_id=123456789):
        self.id = user_id

async def test_real_data():
    """Test with real data from the API."""
    print("=== Testing with Real API Data ===\n")
    
    user = MockUser()
    
    try:
        # Get real library data
        library_data = await get_cached_library_data(user)
        categories = library_data.get('categories', [])
        
        print(f"Total categories found: {len(categories)}")
        print("\nAll categories:")
        for i, cat in enumerate(categories):
            cat_id = cat.get('id', 'NO_ID')
            cat_name = cat.get('name', 'NO_NAME')
            skill_count = len(cat.get('skill_tree', []))
            normalized = normalize_category_id(cat_id)
            print(f"  {i+1:2d}. ID: {cat_id:15} | Normalized: {normalized:15} | Name: {cat_name:25} | Skills: {skill_count}")
        
        print("\n=== Testing Group Mappings ===")
        for group in ['upper', 'lower', 'core']:
            found_categories = find_categories_for_group(categories, group)
            print(f"\n{group.upper()} BODY:")
            print(f"  Expected: {get_category_group_mapping()[group]}")
            print(f"  Found: {found_categories}")
            
            # Test position info for each found category
            for cat_id in found_categories:
                position_info = get_category_position_info(categories, cat_id, group)
                print(f"    {cat_id} -> Position: '{position_info}'")
        
        print("\n=== Testing Navigation Simulation ===")
        # Simulate upper body navigation
        upper_categories = find_categories_for_group(categories, 'upper')
        if upper_categories:
            print(f"\nUpper body categories: {upper_categories}")
            current = upper_categories[0]
            print(f"Starting with: {current}")
            
            for i in range(len(upper_categories) + 2):  # Test wrapping
                position_info = get_category_position_info(categories, current, 'upper')
                print(f"  Step {i}: {current} -> Position: '{position_info}'")
                
                # Simulate next button
                current_index = upper_categories.index(current)
                next_index = (current_index + 1) % len(upper_categories)
                current = upper_categories[next_index]
        
        print("\n=== Testing Specific Categories ===")
        test_categories = ['PUSH', '10', 'PULL', '11', 'SQUAT', '12']
        for test_cat in test_categories:
            normalized = normalize_category_id(test_cat)
            # Find actual category data
            cat_data = None
            for cat in categories:
                if normalize_category_id(cat.get('id', '')) == normalized:
                    cat_data = cat
                    break
            
            if cat_data:
                skill_tree = cat_data.get('skill_tree', [])
                first_skill = skill_tree[0] if skill_tree else None
                skill_name = first_skill.get('name', 'NO_NAME') if first_skill else 'NO_SKILLS'
                print(f"  {test_cat} -> {normalized} -> Found: {cat_data.get('name')} -> First skill: {skill_name}")
            else:
                print(f"  {test_cat} -> {normalized} -> NOT FOUND")
                
    except Exception as e:
        print(f"Error testing real data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_data())