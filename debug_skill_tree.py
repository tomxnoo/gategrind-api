#!/usr/bin/env python3
"""
Debug script to test skill tree navigation logic
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from features.skills.ui.skill_tree_panel import (
    normalize_category_id,
    get_category_group_mapping,
    find_categories_for_group,
    get_category_position_info
)

def test_category_logic():
    """Test the category navigation logic with sample data."""
    print("=== Testing Skill Tree Category Logic ===\n")
    
    # Sample categories data (similar to what comes from API)
    sample_categories = [
        {'id': '10', 'name': 'Push'},
        {'id': '11', 'name': 'Pull'},
        {'id': '12', 'name': 'Squat'},
        {'id': '13', 'name': 'Hinge'},
        {'id': '14', 'name': 'Lunge'},
        {'id': '15', 'name': 'Core'},
        {'id': 'PUSH', 'name': 'Push Movements'},
        {'id': 'PULL', 'name': 'Pull Movements'},
        {'id': 'SQUAT', 'name': 'Squat Movements'},
    ]
    
    print("Sample categories:")
    for cat in sample_categories:
        print(f"  {cat['id']} -> {cat['name']}")
    print()
    
    # Test normalization
    print("=== Testing Category ID Normalization ===")
    test_ids = ['10', '11', '12', 'PUSH', 'push', 'Pull', 'SQUAT']
    for test_id in test_ids:
        normalized = normalize_category_id(test_id)
        print(f"  {test_id} -> {normalized}")
    print()
    
    # Test group mapping
    print("=== Testing Group Mapping ===")
    group_mapping = get_category_group_mapping()
    for group, categories in group_mapping.items():
        print(f"  {group}: {categories}")
    print()
    
    # Test finding categories for each group
    print("=== Testing Find Categories for Group ===")
    for group in ['upper', 'lower', 'core']:
        found = find_categories_for_group(sample_categories, group)
        print(f"  {group}: {found}")
    print()
    
    # Test position info
    print("=== Testing Position Info ===")
    test_cases = [
        ('upper', 'PUSH'),
        ('upper', '10'),  # Should normalize to PUSH
        ('lower', 'SQUAT'),
        ('lower', '12'),  # Should normalize to SQUAT
        ('core', 'CORE'),
        ('core', '15'),   # Should normalize to CORE
    ]
    
    for group, category in test_cases:
        position_info = get_category_position_info(sample_categories, category, group)
        print(f"  Group: {group}, Category: {category} -> Position: '{position_info}'")
    print()

if __name__ == "__main__":
    test_category_logic()