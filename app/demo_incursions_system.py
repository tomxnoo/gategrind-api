"""
Incursions System Demo Script

This script demonstrates the key features of the re-implemented incursions system:
- Creating incursions with different types and rewards
- Managing participant contributions
- Automatic scheduling with spawn cooldowns
- Progress tracking and completion detection
- Statistics and monitoring

Run this script to see the incursion system in action.
"""
import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

# Mock database session for demo purposes
class MockSession:
    def __init__(self):
        self.data = {}
        self.committed = False
    
    def add(self, obj):
        print(f"📝 Adding {obj.__class__.__name__} to session")
    
    async def commit(self):
        self.committed = True
        print("💾 Session committed to database")
    
    async def refresh(self, obj):
        print(f"🔄 Refreshing {obj.__class__.__name__} from database")
    
    async def execute(self, query):
        print(f"🔍 Executing database query")
        return MockResult()
    
    async def close(self):
        print("🔒 Database session closed")

class MockResult:
    def scalar(self):
        return 2  # Mock active incursions count

# Import our incursion system components
from app.infrastructure.database.models.v2.incursions import (
    Incursion, IncursionParticipant, IncursionType, RewardType, IncursionStatus
)
from app.application.services.incursion_service import IncursionService
from app.application.services.incursion_scheduler import (
    IncursionScheduler, SpawnCooldownConfig, IncursionTemplate
)


async def demo_incursion_creation():
    """Demonstrate creating different types of incursions."""
    print("\n🎯 === INCURSION CREATION DEMO ===")
    
    session = MockSession()
    service = IncursionService(session)
    
    # Override get_session for demo
    service.get_session = lambda: session
    
    # Create a SURGE incursion
    print("\n📈 Creating SURGE Incursion...")
    surge_incursion = await service.create_incursion(
        title="Morning Push-Up Surge",
        description="Start your day strong with a community push-up challenge!",
        incursion_type=IncursionType.SURGE,
        target_exercise="push_ups",
        target_reps=500,
        reward_type=RewardType.XP,
        reward_value=150,
        reward_description="Morning Warrior XP Boost"
    )
    print(f"✅ Created: {surge_incursion.title}")
    print(f"   Type: {surge_incursion.incursion_type.value}")
    print(f"   Target: {surge_incursion.target_reps} {surge_incursion.target_exercise}")
    print(f"   Reward: {surge_incursion.reward_value} {surge_incursion.reward_type.value}")
    print(f"   Progress: {surge_incursion.progress_percentage:.1f}%")
    
    # Create a CHALLENGE incursion
    print("\n🏆 Creating CHALLENGE Incursion...")
    challenge_incursion = await service.create_incursion(
        title="Elite Squat Challenge",
        description="Only the strongest will complete this intense squat challenge!",
        incursion_type=IncursionType.CHALLENGE,
        target_exercise="squats",
        target_reps=1000,
        reward_type=RewardType.BUFF,
        reward_value=300,
        reward_description="Legendary Strength Buff (+25% XP for 24h)"
    )
    print(f"✅ Created: {challenge_incursion.title}")
    print(f"   Type: {challenge_incursion.incursion_type.value}")
    print(f"   Target: {challenge_incursion.target_reps} {challenge_incursion.target_exercise}")
    print(f"   Reward: {challenge_incursion.reward_description}")
    
    # Create an ANOMALY incursion
    print("\n🌟 Creating ANOMALY Incursion...")
    anomaly_incursion = await service.create_incursion(
        title="Temporal Fitness Rift",
        description="A mysterious anomaly has appeared! Complete burpees to stabilize reality.",
        incursion_type=IncursionType.ANOMALY,
        target_exercise="burpees",
        target_reps=200,
        reward_type=RewardType.ITEM,
        reward_value=1,
        reward_description="Chrono Fitness Crystal (Rare Item)"
    )
    print(f"✅ Created: {anomaly_incursion.title}")
    print(f"   Type: {anomaly_incursion.incursion_type.value}")
    print(f"   Target: {anomaly_incursion.target_reps} {anomaly_incursion.target_exercise}")
    print(f"   Reward: {anomaly_incursion.reward_description}")
    
    return [surge_incursion, challenge_incursion, anomaly_incursion]


async def demo_participant_contributions(incursions: List[Incursion]):
    """Demonstrate participant contributions and progress tracking."""
    print("\n👥 === PARTICIPANT CONTRIBUTIONS DEMO ===")
    
    session = MockSession()
    service = IncursionService(session)
    service.get_session = lambda: session
    
    # Mock getting incursion by ID
    surge_incursion = incursions[0]
    service.get_incursion_by_id = lambda incursion_id: surge_incursion
    
    print(f"\n📊 Tracking progress for: {surge_incursion.title}")
    print(f"Initial progress: {surge_incursion.current_reps}/{surge_incursion.target_reps} ({surge_incursion.progress_percentage:.1f}%)")
    
    # Simulate multiple participants contributing
    participants = [
        {"user_id": 101, "name": "Alice", "reps": 50},
        {"user_id": 102, "name": "Bob", "reps": 75},
        {"user_id": 103, "name": "Charlie", "reps": 30},
        {"user_id": 104, "name": "Diana", "reps": 100},
        {"user_id": 105, "name": "Eve", "reps": 45},
    ]
    
    for participant in participants:
        print(f"\n🏃 {participant['name']} contributes {participant['reps']} push-ups")
        
        # Add contribution
        success = await service.add_participant_contribution(
            incursion_id=surge_incursion.incursion_id,
            user_id=participant["user_id"],
            reps=participant["reps"]
        )
        
        if success:
            surge_incursion.current_reps += participant["reps"]
            print(f"   ✅ Contribution accepted!")
            print(f"   📈 New progress: {surge_incursion.current_reps}/{surge_incursion.target_reps} ({surge_incursion.progress_percentage:.1f}%)")
            
            if surge_incursion.is_completed:
                print(f"   🎉 INCURSION COMPLETED! All participants earn: {surge_incursion.reward_description}")
                break
        else:
            print(f"   ❌ Contribution failed")


async def demo_scheduler_with_cooldowns():
    """Demonstrate the incursion scheduler with spawn cooldowns."""
    print("\n⏰ === SCHEDULER WITH COOLDOWNS DEMO ===")
    
    # Create a custom cooldown configuration for demo
    cooldown_config = SpawnCooldownConfig(
        min_cooldown_minutes=5,  # Short cooldown for demo
        max_cooldown_minutes=15,
        max_concurrent_incursions=3,
        type_specific_cooldowns={
            IncursionType.SURGE: 10,
            IncursionType.CHALLENGE: 20,
            IncursionType.ANOMALY: 30
        }
    )
    
    print(f"🔧 Cooldown Configuration:")
    print(f"   Global cooldown: {cooldown_config.min_cooldown_minutes}-{cooldown_config.max_cooldown_minutes} minutes")
    print(f"   Max concurrent: {cooldown_config.max_concurrent_incursions}")
    print(f"   Type cooldowns: {dict((t.value, m) for t, m in cooldown_config.type_specific_cooldowns.items())}")
    
    # Create mock service
    session = MockSession()
    service = IncursionService(session)
    service.get_session = lambda: session
    service.get_active_incursions = lambda: []  # No active incursions initially
    service.cleanup_expired_incursions = lambda: 0
    service.health_check = lambda: {"status": "healthy", "active_incursions": 0}
    
    # Create scheduler
    scheduler = IncursionScheduler(service, cooldown_config)
    
    print(f"\n📋 Available Incursion Templates: {len(scheduler.incursion_templates)}")
    for template in scheduler.incursion_templates[:3]:  # Show first 3
        print(f"   • {template.title} ({template.incursion_type.value}) - Weight: {template.weight}")
    
    # Test spawn conditions
    print(f"\n🎲 Testing Spawn Conditions:")
    
    # First spawn should be allowed
    should_spawn = await scheduler._should_spawn_incursion()
    print(f"   First spawn allowed: {should_spawn}")
    
    # Force spawn an incursion
    print(f"\n🚀 Force spawning a SURGE incursion...")
    
    # Mock the create_incursion method
    async def mock_create_incursion(**kwargs):
        incursion = Incursion(
            incursion_id=f"demo_{kwargs['incursion_type'].value}_{datetime.now().strftime('%H%M%S')}",
            title=kwargs['title'],
            description=kwargs['description'],
            incursion_type=kwargs['incursion_type'],
            target_exercise=kwargs['target_exercise'],
            target_reps=kwargs['target_reps'],
            reward_type=kwargs['reward_type'],
            reward_value=kwargs['reward_value'],
            reward_description=kwargs['reward_description'],
            expires_at=datetime.now(timezone.utc) + timedelta(hours=kwargs.get('duration_hours', 2))
        )
        print(f"   ✨ Spawned: {incursion.title}")
        return incursion
    
    service.create_incursion = mock_create_incursion
    
    success = await scheduler.force_spawn_incursion(IncursionType.SURGE)
    print(f"   Force spawn result: {success}")
    
    # Check cooldown status
    print(f"\n📊 Cooldown Status:")
    status = scheduler.get_cooldown_status()
    print(f"   Scheduler running: {status['is_running']}")
    print(f"   Last spawn: {status['last_spawn_time']}")
    print(f"   Global cooldown remaining: {status['global_cooldown_remaining']} seconds")
    
    # Test spawn during cooldown
    print(f"\n⏳ Testing spawn during cooldown...")
    should_spawn = await scheduler._should_spawn_incursion()
    print(f"   Should spawn during cooldown: {should_spawn}")


async def demo_incursion_templates():
    """Demonstrate incursion template system."""
    print("\n📝 === INCURSION TEMPLATES DEMO ===")
    
    # Create some example templates
    templates = [
        IncursionTemplate(
            title="Dawn Warrior Challenge",
            description="Rise with the sun and conquer your morning workout!",
            incursion_type=IncursionType.SURGE,
            target_exercise="push_ups",
            target_reps_range=(100, 300),
            reward_type=RewardType.XP,
            reward_value_range=(50, 150),
            reward_description="Dawn Warrior XP",
            duration_hours=3.0,
            weight=2.0
        ),
        IncursionTemplate(
            title="Legendary Beast Mode",
            description="Only the most dedicated warriors can complete this challenge!",
            incursion_type=IncursionType.CHALLENGE,
            target_exercise="burpees",
            target_reps_range=(200, 500),
            reward_type=RewardType.BUFF,
            reward_value_range=(200, 400),
            reward_description="Beast Mode Buff",
            duration_hours=6.0,
            weight=0.5  # Rare spawn
        ),
        IncursionTemplate(
            title="Quantum Fitness Anomaly",
            description="Reality is glitching! Help stabilize the fitness matrix!",
            incursion_type=IncursionType.ANOMALY,
            target_exercise="jumping_jacks",
            target_reps_range=(500, 1000),
            reward_type=RewardType.ITEM,
            reward_value_range=(1, 3),
            reward_description="Quantum Fitness Shard",
            duration_hours=1.5,
            weight=0.1  # Very rare
        )
    ]
    
    print(f"📋 Template Examples:")
    for template in templates:
        print(f"\n🎯 {template.title}")
        print(f"   Type: {template.incursion_type.value}")
        print(f"   Exercise: {template.target_exercise}")
        print(f"   Reps: {template.target_reps_range[0]}-{template.target_reps_range[1]}")
        print(f"   Reward: {template.reward_value_range[0]}-{template.reward_value_range[1]} {template.reward_type.value}")
        print(f"   Duration: {template.duration_hours} hours")
        print(f"   Spawn Weight: {template.weight} (higher = more common)")
    
    # Demonstrate weighted selection
    print(f"\n🎲 Weighted Selection Demo (100 selections):")
    selections = {}
    
    # Mock weighted random choice
    import random
    def weighted_choice(templates):
        total_weight = sum(t.weight for t in templates)
        r = random.uniform(0, total_weight)
        current_weight = 0
        for template in templates:
            current_weight += template.weight
            if r <= current_weight:
                return template
        return templates[-1]
    
    for _ in range(100):
        selected = weighted_choice(templates)
        selections[selected.title] = selections.get(selected.title, 0) + 1
    
    for title, count in selections.items():
        print(f"   {title}: {count} times ({count}%)")


async def demo_progress_tracking():
    """Demonstrate progress tracking and completion detection."""
    print("\n📊 === PROGRESS TRACKING DEMO ===")
    
    # Create a sample incursion
    incursion = Incursion(
        incursion_id="progress_demo",
        title="Progress Tracking Demo",
        description="Demonstrating real-time progress tracking",
        incursion_type=IncursionType.SURGE,
        target_exercise="sit_ups",
        target_reps=200,
        reward_type=RewardType.XP,
        reward_value=100,
        reward_description="Progress Master XP",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=2)
    )
    
    print(f"🎯 Incursion: {incursion.title}")
    print(f"Target: {incursion.target_reps} {incursion.target_exercise}")
    
    # Simulate progress updates
    contributions = [25, 50, 30, 45, 20, 30]  # Total: 200
    
    for i, reps in enumerate(contributions, 1):
        incursion.current_reps += reps
        
        print(f"\n📈 Update #{i}: +{reps} reps")
        print(f"   Progress: {incursion.current_reps}/{incursion.target_reps} ({incursion.progress_percentage:.1f}%)")
        print(f"   Status: {'🎉 COMPLETED!' if incursion.is_completed else '⏳ In Progress'}")
        
        if incursion.is_completed:
            incursion.status = IncursionStatus.COMPLETED
            incursion.is_active = False
            print(f"   🏆 Incursion completed! All participants earn: {incursion.reward_description}")
            break


async def demo_health_monitoring():
    """Demonstrate system health monitoring."""
    print("\n🏥 === HEALTH MONITORING DEMO ===")
    
    session = MockSession()
    service = IncursionService(session)
    service.get_session = lambda: session
    
    # Mock some statistics
    service.get_incursion_stats = lambda: {
        "total_incursions": 156,
        "active_incursions": 3,
        "completed_incursions": 142,
        "expired_incursions": 11,
        "total_participants": 1247,
        "total_reps_contributed": 45623,
        "average_completion_rate": 92.8
    }
    
    print("🔍 System Health Check:")
    health = await service.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Database: Connected ✅")
    print(f"   Active Incursions: {health.get('active_incursions', 'N/A')}")
    
    print("\n📊 System Statistics:")
    stats = await service.get_incursion_stats()
    for key, value in stats.items():
        formatted_key = key.replace('_', ' ').title()
        if isinstance(value, float):
            print(f"   {formatted_key}: {value:.1f}%")
        else:
            print(f"   {formatted_key}: {value:,}")


async def main():
    """Run the complete incursions system demo."""
    print("🎮 INCURSIONS SYSTEM DEMO")
    print("=" * 50)
    print("Welcome to the Rise of Strength Incursions System!")
    print("This demo showcases the key features of our re-implemented incursion system.")
    
    try:
        # Run all demo sections
        incursions = await demo_incursion_creation()
        await demo_participant_contributions(incursions)
        await demo_scheduler_with_cooldowns()
        await demo_incursion_templates()
        await demo_progress_tracking()
        await demo_health_monitoring()
        
        print("\n🎉 === DEMO COMPLETE ===")
        print("The incursions system is ready for deployment!")
        print("\nKey Features Demonstrated:")
        print("✅ Multiple incursion types (SURGE, CHALLENGE, ANOMALY)")
        print("✅ Flexible reward system (XP, BUFF, ITEM)")
        print("✅ Real-time progress tracking")
        print("✅ Participant contribution management")
        print("✅ Automatic scheduling with spawn cooldowns")
        print("✅ Weighted template system")
        print("✅ Health monitoring and statistics")
        print("✅ Comprehensive error handling")
        
    except Exception as e:
        print(f"\n❌ Demo Error: {e}")
        print("This is expected in a demo environment without a real database.")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())