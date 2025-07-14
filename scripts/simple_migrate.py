
#!/usr/bin/env python3
"""
Simple migration script that won't conflict with running bot
"""
import sys
import json
from pathlib import Path

# Add the RealmOfShadows directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def migrate_health_data():
    """Simple health data migration"""
    print("=== SIMPLE HEALTH DATA MIGRATION ===")
    
    # Check if health file exists
    user_id = 168786415096692736
    health_file = Path("data/health") / f"{user_id}.json"
    
    if not health_file.exists():
        print(f"No health file found for user {user_id}")
        return
    
    try:
        with open(health_file, 'r') as f:
            health_data = json.load(f)
        
        latest_data = health_data.get('latest_data', {})
        steps = latest_data.get('steps', 0)
        walking_reps = steps // 100
        
        print(f"Health data found:")
        print(f"  Steps: {steps:,}")
        print(f"  Walking reps: {walking_reps}")
        print(f"  Active energy: {latest_data.get('active_energy', 0)}")
        print(f"  Sleep hours: {latest_data.get('sleep_hours', 0)}")
        print(f"  Dietary energy: {latest_data.get('dietary_energy', 0)}")
        print()
        print("✅ Health data ready for sync via /logstats endpoint")
        
    except Exception as e:
        print(f"❌ Error reading health file: {e}")

if __name__ == "__main__":
    migrate_health_data()
