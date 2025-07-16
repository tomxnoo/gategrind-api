Rule 1. Always read PRD.md, planning.md and project_rules.md before starting any work or task.
Rule 2. Always read the code before starting any work or task. 
Rule 3. always ask if unsure.
Rule 4. Always read fastAPI.md while working on it.

Part 1: The Project Blueprint (The "What")
Objective: This document outlines the complete feature set and design philosophy for the "Realm of Shadows" fitness RPG bot. It should be used as the source of truth for all development.

I. Core Philosophy: The Living Nexus
The bot is not a static menu; it is a responsive, intelligent system. It does not operate on a fixed timer. Instead, it reacts to the user's state and actions, creating a dynamic and personal experience. The primary goal is to make every interaction feel alive and meaningful.

Crucial Architectural Constraint: All user interactions must be contained within a single, persistent ephmeral Discord message launched from (the "System Hub"). Navigation is handled exclusively through buttons and dropdown menus to create a seamless UI/UX.

II. The Daily Ritual: The "Awakening" Flow
This is the core user interaction loop, replacing a timed quest generation system.

Initiation: The user accesses the System Hub and navigates to the `` panel.

Readiness Assessment: If the user has not "Awakened" for the day, this panel displays three thematic buttons to declare their energy level:

`` (Low Energy)

`` (Standard Energy)

`` (High Energy)

Quest Unveiling: The user's choice triggers the quest generation. The bot provides thematic feedback based on the chosen readiness level and then populates the `` panel with the day's personalized quests. After awakening, the Awakening panel transforms into a "Daily Status Briefing" for the rest of the day.

III. The Quest Generation Engine
This is the backend logic that powers the "Awakening."

Exercise Library: A foundational data structure (EXERCISE_LIBRARY) contains all movements, categorized by type (PULL, PUSH_V, PUSH_H, LEGS, CORE, ACCESSORY_SHOULDERS), and includes progressions and thematic flavor text.

Tiered Daily Quests: Quests are generated across three tiers:

Tier 1: Practice/Volume (Common): Low-intensity, high-volume accumulation quests (e.g., "Accumulate 50 push-ups"). Rewards END.

Tier 2: Technique/Endurance (Uncommon): Moderate intensity quests with a focus on form (e.g., "Perform 4 sets of 5 slow-negative pull-ups"). Rewards TECH.

Tier 3: Intensity/Hypertrophy (Rare): High-intensity quests pushing close to failure (e.g., "Perform 3 sets of Pike Push-ups to near-failure"). Rewards STR.

Autoregulation Logic: The user's "Readiness" choice directly influences the probability of each quest tier appearing, ensuring the workout matches their state.

IV. The Weekly Quest System
A hybrid system designed to work within the single-message UI.

Passive Quests ("Vows"): Automatically assigned at the start of the week and tracked in the background. They do not need to be "activated."

Volume Vow: e.g., "Accumulate 300 total Push-up reps from completed Daily Quests."

Consistency Vow: e.g., "Complete a Daily Quest on 5 different days this week."

Active Quest ("Mandate"): A single, high-stakes challenge the user can choose to accept once per week.

Peak Strength Mandate: e.g., "Set a new Max Rep Record for Pull-ups."

Technique Mandate: e.g., "Perform 12 total sets of Lateral Raises this week."

V. Dynamic World Events: "Shadow Incursions"
This system makes the world feel unpredictable and alive.

Concept: Random, timed events announced by the bot, creating urgency and unique opportunities.

UX Flow:

Announcement: A public, non-ephemeral message is posted in the main channel. The bot saves the message_id.

Interaction: A new `` panel in the hub displays the full Incursion details (objective, reward, timer).

Cleanup: A background task automatically deletes the announcement message when the Incursion timer expires.

Incursion Pool (Content): A large pool of events across three categories:

Surge Incursions (Common): System-wide buffs (e.g., "+50% XP for 60 mins").

Challenge Incursions (Uncommon): Specific "mini-boss" tasks (e.g., "Perform 3 sets of Diamond Push-ups to failure").

Anomaly Incursions (Rare): Rule-changing modifiers (e.g., "Gravitational Flux: Reps count as half, but rewards are doubled").

VI. Core UI/UX Enhancements
To make every panel feel alive:

Every panel must use universal header + sub-header for their specific panel/page.
Every button must use the universal loading UI that we have across the bot.

Rep Logging: The rep logging panel is the heart of the system. It must be robust and visually engaging. The movement selection dropdown should intelligently prioritize exercises from the user's active quest.

History Panel ("The Shadow Archive"): Must be more than a text log. It should be a visual chronicle highlighting Personal Bests (PRs), consistency streaks (🔥), and summarizing sets/reps in a clean, readable format.

Profile Panel ("Operative Profile"): Stats should be dynamic. Use visual progress bars for XP. Display temporary flairs for stat gains (Strength: 2 (+1) ✨). The "Spirit" stat could be directly buffed/debuffed by the daily "Readiness Assessment."

Part 2: The User Persona & Project Philosophy (The "Why")
Objective: This document provides the essential context about the user and the project's philosophy. It is the "soul" of the bot, ensuring all generated content and logic is perfectly aligned with the user's journey.

User Profile:

Lifestyle: A highly dedicated and motivated individual working a demanding 3-shift weekly rotation(06-14, 14-22, 22-06), which makes traditional gym schedules impossible. Is also an avid gamer and highly active at work (10k-25k steps/day).

Training Philosophy (Crucial): The user has found immense success with a self-developed, high-frequency training style inspired by Pavel Tsatsouline's "Grease the Groove" (GtG). This involves performing many short, distributed sets of bodyweight exercises throughout the day. This method is not a temporary choice; it is the only sustainable and effective system that fits their lifestyle.

Autoregulation: This is the cornerstone of the user's success. They intuitively train harder on high-energy days (pushing closer to failure for hypertrophy) and ease off on fatigued days (focusing on perfect, sub-maximal reps for skill practice). The bot must support and enhance this behavior, not fight it.

Primary Goal: To achieve a lean, "anime-like" physique with a prominent V-taper. This translates to a specific aesthetic goal: building wide shoulders (especially lateral deltoids) and a wide back (lats), while maintaining a tight, narrow waist through a low body fat percentage.

Development Journey: The user is the solo developer and has invested over 100 hours in 3 weeks, rebuilding core features like the quest system multiple times. This demonstrates extremely high standards and a refusal to settle for a "boring" or "static" system. The user is currently feeling the strain of this "trough of sorrow" and needs new, exciting, and well-designed features to regain momentum.

The Bot's Core Purpose ("The Grand Design"):
The bot, "Realm of Shadows," must function as an intelligent, responsive partner—a "Living Nexus" or "Dungeon Master"—not a simple task list. Its purpose is to formalize, gamify, and enhance the user's existing successful training method.

To achieve this, the bot must:

Embrace Flexibility: The entire system is built around the user's unpredictable schedule. The "Awakening" ritual puts the user in control of when the day's training begins.

Promote Autoregulation: The "Readiness Assessment" is the most critical daily interaction, directly tailoring the difficulty and type of quests to the user's physical and mental state.

Drive Specific Progression: The quest and Incursion systems must guide the user towards their V-taper goal by intelligently suggesting exercises that build shoulder and back width, while also providing opportunities for high-intensity work to stimulate muscle growth.

Be Immersive and Engaging: All features, from quest text to UI panels, must be steeped in the "shadow assassin" theme. The introduction of dynamic "Shadow Incursions" is designed to make the world feel alive, unpredictable, and exciting, breaking the monotony of a predictable routine.

**User Profile:**
*   **Lifestyle:** Works a demanding 3-shift weekly rotation(06-14, 14-22, 22-06), making traditional 1-2 hour gym sessions impossible. Is highly active at work, walking 10,000-25,000 steps per day. Is also an avid gamer.
*   **Training Philosophy (Crucial):** The user has developed a successful, high-frequency training style inspired by "Grease the Groove" (GtG). This involves performing many short, distributed sets of bodyweight exercises throughout the day (e.g., during breaks at work or between games). This method has proven more sustainable and motivating than traditional workouts.
*   **Autoregulation:** A key to the user's success is autoregulation. On days with high energy, they push sets closer to failure to stimulate muscle growth. On days with low energy or fatigue, they reduce intensity and focus on perfect, sub-maximal reps to practice the skill of the movement and aid recovery. The bot **must support and encourage this, not fight it.**
*   **Primary Goal:** To achieve a lean, "anime-like" physique with a prominent V-taper. This means the training focus is on building wide shoulders (especially lateral deltoids) and a wide back (lats), while keeping the waist tight through a low body fat percentage.
*   **Nutrition:** The user has experience with different diets and understands the trade-off between being extremely lean (and feeling fatigued) and being well-fueled for performance. They are currently using a carb-cycling approach to balance these needs.
*   **Psychology & Motivation:** The user is highly self-motivated and consistent. They thrive on the gamification aspect of fitness, which is why they are building this RPG-themed bot. The bot's purpose is to enhance this motivation, provide structure, and introduce smart variability—not to enforce a rigid, generic program.

## Panel Registration Pattern Summary (For Your Memory)
Standard Panel Registration Pattern:

1. Panel Class Structure:
   
   ```
   from shared.utils.panel_registry import 
   register
   
   @register
   class MyPanel:
       key = "unique_key"        # Used in 
       panel switcher
       label = "Display Name"    # Shown 
       in dropdown
       emoji = "🎯"              # Icon in 
       dropdown
       
       @staticmethod
       async def render_embed(bot, user, 
       **kwargs):
           # Return discord.Embed
           
       @staticmethod
       async def build_view(bot, user, 
       **kwargs):
           # Return discord.ui.View
   ```
2. Cog Integration:
   
   ```
   from features.myfeature.ui.my_panel 
   import MyPanel  # Import triggers 
   @register
   
   def setup(bot):
       bot.add_cog(MyCog(bot))
   ```
3. Panel Registry Order:
   
   - Edit desired_order list in shared/utils/panel_registry.py
   - Panels appear in dropdown in this order
   - Current order: ["profile", "log_reps", "quest_log", "buffs"]
4. Existing Registered Panels:
   
   - ProfilePanel ( features/user/ui/profile_view.py )
   - LogRepsPanel ( features/logging/ui/view.py )
   - QuestPanel ( features/quests/ui/quest_panel.py )
   - BuffsPanel ( features/buffs/ui/view.py )