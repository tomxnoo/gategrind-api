import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from features.incursions.models.incursion import IncursionType, RewardType

class IncursionContentGenerator:
    """Generates thematic content for Shadow Incursions"""
    
    # Content templates organized by incursion type
    SURGE_TEMPLATES = [
        {
            "title": "🌊 Crimson Tide Surge",
            "description": "The shadows pulse with ancient energy, amplifying all training efforts. Strike while the darkness flows through you!",
            "effect": "All XP gains increased by 50% for the next 60 minutes",
            "target_exercise": "any",
            "target_reps": 0,  # No specific target for surge events
            "reward_type": RewardType.XP,
            "reward_value": 50,  # 50% XP boost
            "duration_hours": 1
        },
        {
            "title": "⚡ Lightning Reflexes Surge",
            "description": "Electric energy crackles through the realm. Your movements become swift and precise!",
            "effect": "All exercises grant +1 bonus rep for progression tracking",
            "target_exercise": "any",
            "target_reps": 0,
            "reward_type": RewardType.BUFF,
            "reward_value": 1,
            "duration_hours": 2
        },
        {
            "title": "🔥 Infernal Focus Surge",
            "description": "The fires of determination burn bright. Channel this intensity into your training!",
            "effect": "Next 3 completed quests grant double STR/END/SPR XP",
            "target_exercise": "any",
            "target_reps": 0,
            "reward_type": RewardType.BUFF,
            "reward_value": 2,
            "duration_hours": 4
        }
    ]
    
    CHALLENGE_TEMPLATES = [
        {
            "title": "💀 Shadow Wraith Challenge",
            "description": "A spectral enemy emerges from the void. Prove your upper body dominance to banish it back to the shadows!",
            "target_exercise": "pull_ups",
            "target_reps": 100,
            "reward_type": RewardType.XP,
            "reward_value": 300,
            "duration_hours": 6
        },
        {
            "title": "🗡️ Blade Master's Trial",
            "description": "The ancient blade masters test your pushing power. Show them the strength of your resolve!",
            "target_exercise": "push_ups",
            "target_reps": 150,
            "reward_type": RewardType.XP,
            "reward_value": 250,
            "duration_hours": 8
        },
        {
            "title": "🏔️ Mountain's Endurance",
            "description": "The mountain spirits challenge your leg strength. Climb to new heights of power!",
            "target_exercise": "squats",
            "target_reps": 200,
            "reward_type": RewardType.XP,
            "reward_value": 275,
            "duration_hours": 12
        },
        {
            "title": "🌪️ Tempest Core Trial",
            "description": "Chaotic winds test your stability. Prove your core is unshakeable!",
            "target_exercise": "plank_seconds",
            "target_reps": 600,  # 10 minutes total
            "reward_type": RewardType.XP,
            "reward_value": 200,
            "duration_hours": 6
        }
    ]
    
    ANOMALY_TEMPLATES = [
        {
            "title": "🌀 Gravitational Flux",
            "description": "Reality bends around you. Reps are harder to achieve, but the rewards are magnificent!",
            "effect": "All reps count as 0.5x, but XP rewards are doubled",
            "target_exercise": "any",
            "target_reps": 0,
            "reward_type": RewardType.BUFF,
            "reward_value": 200,  # 200% XP multiplier
            "duration_hours": 3,
            "metadata": {"rep_multiplier": 0.5, "xp_multiplier": 2.0}
        },
        {
            "title": "⏰ Temporal Acceleration",
            "description": "Time moves differently in the shadow realm. Quick bursts of activity yield exponential gains!",
            "effect": "Sets of 10+ reps in under 30 seconds grant triple XP",
            "target_exercise": "any",
            "target_reps": 0,
            "reward_type": RewardType.BUFF,
            "reward_value": 300,
            "duration_hours": 2,
            "metadata": {"speed_bonus": True, "time_limit": 30}
        },
        {
            "title": "🎭 Mirror Dimension",
            "description": "Your reflection challenges you to a duel. Every rep must be matched by its mirror!",
            "effect": "All exercises must be performed in pairs (2x reps), but grant 150% XP",
            "target_exercise": "any",
            "target_reps": 0,
            "reward_type": RewardType.BUFF,
            "reward_value": 150,
            "duration_hours": 4,
            "metadata": {"pair_requirement": True, "xp_multiplier": 1.5}
        }
    ]
    
    # Exercise mappings for V-taper focus
    V_TAPER_EXERCISES = {
        "pull_ups": {"category": "back_width", "priority": "high"},
        "chin_ups": {"category": "back_width", "priority": "high"},
        "wide_grip_pull_ups": {"category": "back_width", "priority": "very_high"},
        "lateral_raises": {"category": "shoulder_width", "priority": "very_high"},
        "pike_push_ups": {"category": "shoulder_width", "priority": "high"},
        "handstand_push_ups": {"category": "shoulder_width", "priority": "high"},
        "push_ups": {"category": "chest_shoulders", "priority": "medium"},
        "diamond_push_ups": {"category": "triceps", "priority": "medium"},
        "squats": {"category": "legs", "priority": "low"},
        "lunges": {"category": "legs", "priority": "low"},
        "plank_seconds": {"category": "core", "priority": "medium"}
    }
    
    def generate_surge_incursion(self) -> Dict:
        """Generate a random surge incursion"""
        template = random.choice(self.SURGE_TEMPLATES)
        incursion_id = f"SURGE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "incursion_id": incursion_id,
            "incursion_type": IncursionType.SURGE,
            "title": template["title"],
            "description": template["description"],
            "target_exercise": template["target_exercise"],
            "target_reps": template["target_reps"],
            "reward_type": template["reward_type"],
            "reward_value": template["reward_value"],
            "reward_description": template["effect"],
            "duration_hours": template["duration_hours"],
            "metadata": template.get("metadata", {})
        }
    
    def generate_challenge_incursion(self, focus_v_taper: bool = True) -> Dict:
        """Generate a challenge incursion, optionally focused on V-taper development"""
        if focus_v_taper:
            # Prioritize V-taper exercises
            v_taper_templates = [
                t for t in self.CHALLENGE_TEMPLATES 
                if t["target_exercise"] in self.V_TAPER_EXERCISES
                and self.V_TAPER_EXERCISES[t["target_exercise"]]["priority"] in ["high", "very_high"]
            ]
            template = random.choice(v_taper_templates if v_taper_templates else self.CHALLENGE_TEMPLATES)
        else:
            template = random.choice(self.CHALLENGE_TEMPLATES)
        
        incursion_id = f"CHALLENGE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Add some randomization to target reps (±20%)
        base_reps = template["target_reps"]
        variation = random.uniform(0.8, 1.2)
        target_reps = int(base_reps * variation)
        
        return {
            "incursion_id": incursion_id,
            "incursion_type": IncursionType.CHALLENGE,
            "title": template["title"],
            "description": template["description"],
            "target_exercise": template["target_exercise"],
            "target_reps": target_reps,
            "reward_type": template["reward_type"],
            "reward_value": template["reward_value"],
            "reward_description": f"{template['reward_value']} XP for completing the challenge",
            "duration_hours": template["duration_hours"],
            "metadata": {"base_reps": base_reps, "variation": variation}
        }
    
    def generate_anomaly_incursion(self) -> Dict:
        """Generate a reality-bending anomaly incursion"""
        template = random.choice(self.ANOMALY_TEMPLATES)
        incursion_id = f"ANOMALY_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "incursion_id": incursion_id,
            "incursion_type": IncursionType.ANOMALY,
            "title": template["title"],
            "description": template["description"],
            "target_exercise": template["target_exercise"],
            "target_reps": template["target_reps"],
            "reward_type": template["reward_type"],
            "reward_value": template["reward_value"],
            "reward_description": template["effect"],
            "duration_hours": template["duration_hours"],
            "metadata": template.get("metadata", {})
        }
    
    def generate_random_incursion(self, v_taper_bias: float = 0.7) -> Dict:
        """Generate a random incursion with weighted probabilities"""
        # Weighted probabilities: Surge (50%), Challenge (35%), Anomaly (15%)
        incursion_type = random.choices(
            ["surge", "challenge", "anomaly"],
            weights=[50, 35, 15]
        )[0]
        
        if incursion_type == "surge":
            return self.generate_surge_incursion()
        elif incursion_type == "challenge":
            # 70% chance to focus on V-taper exercises
            focus_v_taper = random.random() < v_taper_bias
            return self.generate_challenge_incursion(focus_v_taper)
        else:
            return self.generate_anomaly_incursion()