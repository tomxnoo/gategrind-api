#!/usr/bin/env python3
"""
Run the comprehensive seeding script from scripts/seed.py
This will populate all movement categories, skill tree nodes, and movements.
"""

import subprocess
import sys
import os

def main():
    print("=" * 70)
    print("RUNNING COMPREHENSIVE SKILL TREE SEEDING")
    print("=" * 70)
    print()
    print("This will use the existing scripts/seed.py which contains:")
    print("- 18 movement categories")
    print("- 90 skill tree nodes (5 levels per category)")
    print("- 200+ movements with proper XP values")
    print()
    
    # Change to the scripts directory
    scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    
    try:
        # Run the comprehensive seeding script
        result = subprocess.run(
            [sys.executable, 'seed.py'],
            cwd=scripts_dir,
            capture_output=True,
            text=True
        )
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("Errors:", result.stderr)
            
        if result.returncode == 0:
            print("\n✅ Seeding completed successfully!")
            print("\nNext steps:")
            print("1. Restart your application")
            print("2. Test the Skill Tree panel")
            print("3. You should now see all categories, nodes, and movements")
        else:
            print("\n❌ Seeding failed with return code:", result.returncode)
            
    except Exception as e:
        print(f"\n❌ Error running seeding script: {e}")
        print("\nTrying direct execution...")
        
        # If subprocess fails, try direct import and execution
        try:
            sys.path.insert(0, scripts_dir)
            import seed
            import asyncio
            
            # Run the seed_data function directly
            asyncio.run(seed.seed_data())
            print("\n✅ Direct seeding completed successfully!")
            
        except Exception as e2:
            print(f"\n❌ Direct execution also failed: {e2}")

if __name__ == "__main__":
    main()