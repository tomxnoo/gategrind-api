#!/usr/bin/env python3

# Simple test to check if the bot is running and what data it has
import requests
import json

def test_api_connection():
    """Test if the API is running and what data it returns."""
    try:
        # Test basic API connection
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"API Health Check: {response.status_code}")
        
        # Test movement library endpoint (this might require auth)
        # We'll just check if the endpoint exists
        try:
            response = requests.get("http://localhost:5000/api/movement-library", timeout=5)
            print(f"Movement Library Endpoint: {response.status_code}")
            if response.status_code == 401:
                print("  -> Requires authentication (expected)")
            elif response.status_code == 200:
                data = response.json()
                print(f"  -> Data available: {len(data.get('categories', []))} categories")
        except Exception as e:
            print(f"Movement Library Endpoint Error: {e}")
            
    except Exception as e:
        print(f"API Connection Error: {e}")

def test_category_logic():
    """Test the category logic with sample data."""
    print("\n=== Testing Category Logic ===")
    
    # Sample categories that might be returned by the API
    sample_categories = [
        {"id": "10", "name": "Push Movements"},
        {"id": "11", "name": "Pull Movements"}, 
        {"id": "12", "name": "Squat Movements"},
        {"id": "13", "name": "Hinge Movements"},
        {"id": "14", "name": "Lunge Movements"},
        {"id": "15", "name": "Core Movements"},
        {"id": "PUSH", "name": "Push"},
        {"id": "PULL", "name": "Pull"},
        {"id": "SQUAT", "name": "Squat"},
    ]
    
    def normalize_category_id(category_id: str) -> str:
        """Normalize category ID to handle different formats from the API."""
        if not category_id:
            return ""
        
        # Convert to uppercase and handle common variations
        normalized = str(category_id).upper().strip()
        
        # Handle numeric to string mapping (legacy database IDs)
        numeric_mapping = {
            "10": "PUSH",
            "11": "PULL", 
            "12": "SQUAT",
            "13": "HINGE",
            "14": "LUNGE",
            "15": "CORE",
        }
        
        if normalized in numeric_mapping:
            return numeric_mapping[normalized]
        
        return normalized
    
    def get_category_group_mapping():
        """Get the mapping of category groups to their category IDs."""
        return {
            'upper': ['PUSH', 'PULL', 'PULL_VERTICAL', 'UPPER_DYNAMIC', 'GRIP', 'BALLISTIC'],
            'lower': ['SQUAT', 'LUNGE', 'HINGE', 'GAIT', 'LOADED_CARRY'],
            'core': ['CORE', 'ROTATION', 'BALANCE', 'FLEXIBILITY', 'MOBILITY_FLOW']
        }
    
    def find_categories_for_group(categories, group: str):
        """Find all category IDs that belong to a specific group - FIXED VERSION."""
        group_mapping = get_category_group_mapping()
        expected_categories = group_mapping.get(group, [])
        
        found_categories = []
        all_category_ids = []
        
        for cat in categories:
            cat_id = cat.get('id', '')
            cat_name = cat.get('name', '').lower()
            
            # Normalize the category ID
            normalized_id = normalize_category_id(cat_id)
            all_category_ids.append(f"{cat_id} -> {normalized_id}")
            
            # Check if this category belongs to the group
            if normalized_id in expected_categories:
                if normalized_id not in found_categories:  # FIXED: Avoid duplicates
                    found_categories.append(normalized_id)
            else:
                # Fallback: check by name patterns for robustness
                if group == 'upper':
                    if any(keyword in cat_name for keyword in ['push', 'pull', 'overhead', 'upper', 'grip', 'ballistic']):
                        if normalized_id not in found_categories:  # FIXED: Avoid duplicates
                            found_categories.append(normalized_id)
                elif group == 'lower':
                    if any(keyword in cat_name for keyword in ['squat', 'lunge', 'hinge', 'leg', 'hip', 'gait', 'carry']):
                        if normalized_id not in found_categories:  # FIXED: Avoid duplicates
                            found_categories.append(normalized_id)
                elif group == 'core':
                    if any(keyword in cat_name for keyword in ['core', 'rotation', 'balance', 'flexibility', 'mobility']):
                        if normalized_id not in found_categories:  # FIXED: Avoid duplicates
                            found_categories.append(normalized_id)
        
        print(f"Category mapping for group '{group}': {all_category_ids}")
        print(f"Found categories for group '{group}': {found_categories}")
        
        return found_categories
    
    print("Sample categories:")
    for cat in sample_categories:
        normalized = normalize_category_id(cat['id'])
        print(f"  {cat['id']} -> {normalized} ({cat['name']})")
    
    print("\nGroup mappings:")
    for group in ['upper', 'lower', 'core']:
        found = find_categories_for_group(sample_categories, group)
        print(f"  {group}: {found}")

if __name__ == "__main__":
    print("=== Skill Tree Debug Test ===")
    test_api_connection()
    test_category_logic()