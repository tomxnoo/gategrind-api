Enhanced logging initialized successfully
✓ Enhanced logging configured - WARN and ERROR messages will now stand out!
[INFO] Starting Discord bot...
INFO:     Started server process [3244]
INFO:     Waiting for application startup.
[INFO] Starting FastAPI application...
[INFO] Initializing database connection pool...
[OK] Database connection pool created successfully.
[INFO] 2025-07-30 18:07:09 [INFO] core.redis_cache
Connected to Redis at rediss://default:AUwGAAIjcDFhZDU1MWI2NjVmMzY0ZTFjOTIzNDU1MDRmM2M3Mjc0M3AxMA@vocal-meerkat-19462.upstash.io:6379
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
[OK] Connected to Redis successfully.
[OK] FastAPI application startup complete.
[OK] Database connection pool created successfully.
[INFO] Connecting to Redis...
[INFO] 2025-07-30 18:07:09 [INFO] core.redis_cache
Connected to Redis at rediss://default:AUwGAAIjcDFhZDU1MWI2NjVmMzY0ZTFjOTIzNDU1MDRmM2M3Mjc0M3AxMA@vocal-meerkat-19462.upstash.io:6379
[OK] Connected to Redis successfully.
[INFO] Pre-loading panel registrations...
[API_CLIENT] Using base URL: http://localhost:5000/api
[API_CLIENT] Created new singleton instance for APIClient
[OK] Skill Tree panel loaded
[DEBUG] Registered panels: ['awakening', 'dungeons', 'profile', 'profile_v2', 'log_reps', 'buffs', 'incursions', 'skill_tree']
[DEBUG] Panel 'awakening': EnhancedAwakeningPanel
[DEBUG] Panel 'dungeons': DungeonPanel
[DEBUG] Panel 'profile': ProfilePanel
[DEBUG] Panel 'profile_v2': ProfileV2Panel
[DEBUG] Panel 'log_reps': LogRepsPanel
[DEBUG] Panel 'buffs': BuffsPanel
[DEBUG] Panel 'incursions': IncursionPanel
[DEBUG] Panel 'skill_tree': SkillTreePanel
[OK] All panels pre-loaded and registered
[INFO] Loading Discord bot extensions...
[OK] features.system.system_hub_cog
[OK] features.awakening.cog
[OK] features.buffs.cog
[OK] features.logging.cog
[OK] features.quests.cog
[OK] features.user.cog
[OK] features.moderation.message_management_cog
[OK] features.moderation.reroll_reset_cog
[OK] features.moderation.quest_completion_cog
✅ Fitness sync cog loaded (event-driven mode)
[OK] features.fitness.fitness_sync_cog
[OK] features.fitness.fitness_api_cog
[OK] features.incursions.cog
INFO:     172.31.86.162:49448 - "GET / HTTP/1.1" 200 OK
════════════════════════════════════════════════════════════
🌒 The System#1314 online • ID 1386656478877716601
Guilds: 1  •  Cogs: 12
════════════════════════════════════════════════════════════
INFO:     127.0.0.1:57628 - "GET /api/v2/auth/health HTTP/1.1" 200 OK
[INFO] 2025-07-30 18:07:12 [INFO] httpx
HTTP Request: GET http://localhost:5000/api/v2/auth/health "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/auth/health
[OK] API Health Check: healthy - RoS-TRAE V2 API v2.0.0
[INFO] API Base URL: http://localhost:5000/api
[INFO] Development Mode: False
[OK] System Hub persistent view added
[INFO] 2025-07-30 18:07:13 [INFO] features.incursions.logic.scheduler
Loaded scheduler settings: testing_mode=True, auto_start=False, announcement_channel=1390756464250847353
[DEBUG] Successfully sent login message on attempt 1
[DEBUG] Starting login work with caching...
[API_CLIENT] Returning existing singleton instance for APIClient
[API_CLIENT] User 168786415096692736 not in registered cache, ensuring registration
[DEBUG] Edited ephemeral login embed with 1 dots at 0.00 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 0.74 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 1.41 seconds
[DEBUG] Edited ephemeral login embed with 1 dots at 2.21 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 3.01 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 3.72 seconds
INFO:     127.0.0.1:45768 - "POST /api/v2/auth/login HTTP/1.1" 200 OK
[INFO] 2025-07-30 18:07:30 [INFO] httpx
HTTP Request: POST http://localhost:5000/api/v2/auth/login "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/auth/login
[API_CLIENT] User aqpq logged in successfully
[API_CLIENT] Attempting login for registered user 168786415096692736
[DEBUG] Edited ephemeral login embed with 1 dots at 4.54 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 5.45 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 6.15 seconds
INFO:     127.0.0.1:45778 - "POST /api/v2/auth/login HTTP/1.1" 200 OK
[INFO] 2025-07-30 18:07:32 [INFO] httpx
HTTP Request: POST http://localhost:5000/api/v2/auth/login "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/auth/login
[API_CLIENT] Successfully obtained token from login for user 168786415096692736
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
[INFO] 2025-07-30 18:07:32 [INFO] app.api.v2.dependencies.auth
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
[INFO] 2025-07-30 18:07:32 [INFO] app.api.v2.dependencies.auth
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
[DEBUG] Edited ephemeral login embed with 1 dots at 7.00 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 7.64 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 8.36 seconds
INFO:     127.0.0.1:45792 - "GET /api/v2/profiles/me HTTP/1.1" 200 OK
[INFO] 2025-07-30 18:07:34 [INFO] httpx
HTTP Request: GET http://localhost:5000/api/v2/profiles/me "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/profiles/me
[DEBUG] Registered panels: ['awakening', 'dungeons', 'profile', 'profile_v2', 'log_reps', 'buffs', 'incursions', 'skill_tree']
[DEBUG] Panel 'awakening': EnhancedAwakeningPanel
[DEBUG] Panel 'dungeons': DungeonPanel
[DEBUG] Panel 'profile': ProfilePanel
[DEBUG] Panel 'profile_v2': ProfileV2Panel
[DEBUG] Panel 'log_reps': LogRepsPanel
[DEBUG] Panel 'buffs': BuffsPanel
[DEBUG] Panel 'incursions': IncursionPanel
[DEBUG] Panel 'skill_tree': SkillTreePanel
[DEBUG] Panel options: [('Profile', 'profile'), ('Profile V2', 'profile_v2'), ('Awakening', 'awakening'), ('Skill Tree', 'skill_tree'), ('Dungeons', 'dungeons'), ('Log Reps', 'log_reps'), ('Buffs & Consumables', 'buffs'), ('Shadow Incursions', 'incursions')]
[DEBUG] Pre-caching skill tree data...
[INFO] 2025-07-30 18:07:34 [INFO] features.skills.ui.skill_tree_panel
Fetching fresh library data...
[API_CLIENT] Returning existing singleton instance for APIClient
[API_CLIENT] Using cached valid token for user 168786415096692736
[INFO] 2025-07-30 18:07:34 [INFO] app.api.v2.movements
Fetching complete skill tree library
[DEBUG] Edited ephemeral login embed with 1 dots at 9.00 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 9.69 seconds
[INFO] 2025-07-30 18:07:37 [INFO] MovementService
Successfully fetched skill tree library with 39 categories
[INFO] 2025-07-30 18:07:37 [INFO] app.api.v2.movements
Successfully returned skill tree library with 39 categories
[DEBUG] Edited ephemeral login embed with 3 dots at 10.49 seconds
INFO:     127.0.0.1:45798 - "GET /api/v2/movements/library HTTP/1.1" 200 OK
[INFO] 2025-07-30 18:07:37 [INFO] httpx
HTTP Request: GET http://localhost:5000/api/v2/movements/library "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/movements/library
[INFO] 2025-07-30 18:07:37 [INFO] features.skills.ui.skill_tree_panel
Fetching fresh profile data for user 168786415096692736...
[API_CLIENT] Returning existing singleton instance for APIClient
[API_CLIENT] Using cached valid token for user 168786415096692736
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
[INFO] 2025-07-30 18:07:37 [INFO] app.api.v2.dependencies.auth
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
[INFO] 2025-07-30 18:07:37 [INFO] app.api.v2.dependencies.auth
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
[DEBUG] Edited ephemeral login embed with 1 dots at 12.50 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 13.15 seconds
INFO:     127.0.0.1:35656 - "GET /api/v2/profiles/me HTTP/1.1" 200 OK
[INFO] 2025-07-30 18:07:39 [INFO] httpx
HTTP Request: GET http://localhost:5000/api/v2/profiles/me "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/profiles/me
[DEBUG] Caching completed successfully
[DEBUG] System hub embed and view built successfully
[DEBUG] Work task completed successfully
[DEBUG] Login animation and work completed successfully
[DEBUG] Successfully updated login message with final result
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
build_skill_tree_embed called for user 168786415096692736 with view_mode=overview, category=None, current_group=None
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Using cached library data (age: 5.9s)
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Successfully retrieved library data for user 168786415096692736
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Using cached profile data for user 168786415096692736 (age: 4.2s)
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Successfully retrieved profile data for user 168786415096692736
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Both data sources available for user 168786415096692736, building full embed with view_mode=overview
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Starting _build_full_skill_tree_embed for user 168786415096692736, category=None, view_mode=overview
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Generated headers successfully for user 168786415096692736
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Found 39 categories for user 168786415096692736
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Profile data keys for user 168786415096692736: ['username', 'id', 'discord_id', 'stats', 'available_points', 'dungeon_progress', 'dungeon_keys', 'unlocked_skills', 'active_quests', 'created_at', 'updated_at']
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Profile data structure for user 168786415096692736: {'username': 'aqpq', 'id': 1, 'discord_id': '168786415096692736', 'stats': {'str_level': 1, 'str_xp': 0.0, 'end_level': 1, 'end_xp': 0.0, 'tech_level': 1, 'tech_xp': 0.0}, 'available_points': {'strength': 4, 'endurance': 4, 'technique': 4}, 'dungeon_progress': None, 'dungeon_keys': [], 'unlocked_skills': [{'ascendant_id': 1, 'node_id': 'push_1', 'unlocked_at': '2025-07-29T15:04:12.886692Z', 'id': 1}, {'ascendant_id': 1, 'node_id': 'upper_dynamic_1', 'unlocked_at': '2025-07-29T20:03:06.302745Z', 'id': 15}, {'ascendant_id': 1, 'node_id': 'core_1', 'unlocked_at': '2025-07-30T13:31:56.323967Z', 'id': 16}], 'active_quests': [], 'created_at': '2025-07-28T19:08:10.876090Z', 'updated_at': '2025-07-30T13:31:56.323967Z'}
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Raw unlocked_skills data for user 168786415096692736: [{'ascendant_id': 1, 'node_id': 'push_1', 'unlocked_at': '2025-07-29T15:04:12.886692Z', 'id': 1}, {'ascendant_id': 1, 'node_id': 'upper_dynamic_1', 'unlocked_at': '2025-07-29T20:03:06.302745Z', 'id': 15}, {'ascendant_id': 1, 'node_id': 'core_1', 'unlocked_at': '2025-07-30T13:31:56.323967Z', 'id': 16}]
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Type of unlocked_skills: <class 'list'>
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Type of first skill: <class 'dict'>
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
First skill data: {'ascendant_id': 1, 'node_id': 'push_1', 'unlocked_at': '2025-07-29T15:04:12.886692Z', 'id': 1}
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
First skill dict keys: dict_keys(['ascendant_id', 'node_id', 'unlocked_at', 'id'])
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Processed unlocked_skill_ids for user 168786415096692736: {'core_1', 'upper_dynamic_1', 'push_1'}
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
User stats for user 168786415096692736: {'str_level': 1, 'str_xp': 0.0, 'end_level': 1, 'end_xp': 0.0, 'tech_level': 1, 'tech_xp': 0.0}
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Available points for user 168786415096692736: {'strength': 4, 'endurance': 4, 'technique': 4}
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
User 168786415096692736 has 3 unlocked skills
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Processing overview mode for user 168786415096692736
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Content length before truncation check: 966 chars
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Successfully created SkillTreePanel embed for user 168786415096692736
[DEBUG] Registered panels: ['awakening', 'dungeons', 'profile', 'profile_v2', 'log_reps', 'buffs', 'incursions', 'skill_tree']
[DEBUG] Panel 'awakening': EnhancedAwakeningPanel
[DEBUG] Panel 'dungeons': DungeonPanel
[DEBUG] Panel 'profile': ProfilePanel
[DEBUG] Panel 'profile_v2': ProfileV2Panel
[DEBUG] Panel 'log_reps': LogRepsPanel
[DEBUG] Panel 'buffs': BuffsPanel
[DEBUG] Panel 'incursions': IncursionPanel
[DEBUG] Panel 'skill_tree': SkillTreePanel
[DEBUG] Panel options: [('Profile', 'profile'), ('Profile V2', 'profile_v2'), ('Awakening', 'awakening'), ('Skill Tree', 'skill_tree'), ('Dungeons', 'dungeons'), ('Log Reps', 'log_reps'), ('Buffs & Consumables', 'buffs'), ('Shadow Incursions', 'incursions')]
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Successfully added panel dropdown for user 168786415096692736
[INFO] 2025-07-30 18:07:43 [INFO] features.skills.ui.skill_tree_panel
Successfully created SkillTreeView for user 168786415096692736
[DEBUG] Edited loading embed with 1 dots at 0.00 seconds
[DEBUG] Edited loading embed with 2 dots at 0.81 seconds
[DEBUG] Edited loading embed with 3 dots at 1.28 seconds
[DEBUG] Animation loop completed after 1.88 seconds
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Using cached library data (age: 10.3s)
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
build_skill_tree_embed called for user 168786415096692736 with view_mode=overview, category=10, current_group=upper
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Using cached library data (age: 10.3s)
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Successfully retrieved library data for user 168786415096692736
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Using cached profile data for user 168786415096692736 (age: 8.5s)
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Successfully retrieved profile data for user 168786415096692736
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Both data sources available for user 168786415096692736, building full embed with view_mode=overview
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Starting _build_full_skill_tree_embed for user 168786415096692736, category=10, view_mode=overview
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Generated headers successfully for user 168786415096692736
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Found 39 categories for user 168786415096692736
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Profile data keys for user 168786415096692736: ['username', 'id', 'discord_id', 'stats', 'available_points', 'dungeon_progress', 'dungeon_keys', 'unlocked_skills', 'active_quests', 'created_at', 'updated_at']
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Profile data structure for user 168786415096692736: {'username': 'aqpq', 'id': 1, 'discord_id': '168786415096692736', 'stats': {'str_level': 1, 'str_xp': 0.0, 'end_level': 1, 'end_xp': 0.0, 'tech_level': 1, 'tech_xp': 0.0}, 'available_points': {'strength': 4, 'endurance': 4, 'technique': 4}, 'dungeon_progress': None, 'dungeon_keys': [], 'unlocked_skills': [{'ascendant_id': 1, 'node_id': 'push_1', 'unlocked_at': '2025-07-29T15:04:12.886692Z', 'id': 1}, {'ascendant_id': 1, 'node_id': 'upper_dynamic_1', 'unlocked_at': '2025-07-29T20:03:06.302745Z', 'id': 15}, {'ascendant_id': 1, 'node_id': 'core_1', 'unlocked_at': '2025-07-30T13:31:56.323967Z', 'id': 16}], 'active_quests': [], 'created_at': '2025-07-28T19:08:10.876090Z', 'updated_at': '2025-07-30T13:31:56.323967Z'}
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Raw unlocked_skills data for user 168786415096692736: [{'ascendant_id': 1, 'node_id': 'push_1', 'unlocked_at': '2025-07-29T15:04:12.886692Z', 'id': 1}, {'ascendant_id': 1, 'node_id': 'upper_dynamic_1', 'unlocked_at': '2025-07-29T20:03:06.302745Z', 'id': 15}, {'ascendant_id': 1, 'node_id': 'core_1', 'unlocked_at': '2025-07-30T13:31:56.323967Z', 'id': 16}]
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Type of unlocked_skills: <class 'list'>
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Type of first skill: <class 'dict'>
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
First skill data: {'ascendant_id': 1, 'node_id': 'push_1', 'unlocked_at': '2025-07-29T15:04:12.886692Z', 'id': 1}
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
First skill dict keys: dict_keys(['ascendant_id', 'node_id', 'unlocked_at', 'id'])
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Processed unlocked_skill_ids for user 168786415096692736: {'core_1', 'upper_dynamic_1', 'push_1'}
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
User stats for user 168786415096692736: {'str_level': 1, 'str_xp': 0.0, 'end_level': 1, 'end_xp': 0.0, 'tech_level': 1, 'tech_xp': 0.0}
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Available points for user 168786415096692736: {'strength': 4, 'endurance': 4, 'technique': 4}
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
User 168786415096692736 has 3 unlocked skills
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Processing category view for user 168786415096692736, category=10
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Finding categories for group 'upper', expecting: ['PUSH', 'PULL', 'PULL_VERTICAL', 'UPPER_DYNAMIC', 'GRIP', 'BALLISTIC']
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Found 6 categories for group 'upper': ['PUSH', 'PULL', 'PULL_VERTICAL', 'UPPER_DYNAMIC', 'GRIP', 'BALLISTIC']
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Skill tree for Push: 5 nodes
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Sample skill node: {'id': 'push_1', 'level': 1, 'name': 'Push - Foundation', 'description': 'Basic movements and fundamental skills for push movements', 'requirements': {'ascendant_level': 1, 'str_points': 0, 'end_points': 0, 'tech_points': 0}, 'movements': [{'id': 33, 'name': 'Push-up', 'xp_per_rep': 1.0, 'stat_reward_type': 'STR'}]}
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Node 0: level=1, name=Push - Foundation
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Node 1: level=2, name=Push - Development
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Node 2: level=3, name=Push - Proficiency
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
After sorting: levels = [1, 2, 3, 4, 5]
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Added level line for Level 1: content length now 690 chars
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Added level line for Level 2: content length now 732 chars
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Added level line for Level 3: content length now 838 chars
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Added level line for Level 4: content length now 942 chars
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Added level line for Level 5: content length now 1054 chars
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Finding categories for group 'upper', expecting: ['PUSH', 'PULL', 'PULL_VERTICAL', 'UPPER_DYNAMIC', 'GRIP', 'BALLISTIC']
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Found 6 categories for group 'upper': ['PUSH', 'PULL', 'PULL_VERTICAL', 'UPPER_DYNAMIC', 'GRIP', 'BALLISTIC']
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Skill tree for Push: 5 nodes
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Sample skill node: {'id': 'push_1', 'level': 1, 'name': 'Push - Foundation', 'description': 'Basic movements and fundamental skills for push movements', 'requirements': {'ascendant_level': 1, 'str_points': 0, 'end_points': 0, 'tech_points': 0}, 'movements': [{'id': 33, 'name': 'Push-up', 'xp_per_rep': 1.0, 'stat_reward_type': 'STR'}]}
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Node 0: level=1, name=Push - Foundation
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Node 1: level=2, name=Push - Development
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Node 2: level=3, name=Push - Proficiency
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
After sorting: levels = [1, 2, 3, 4, 5]
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Content length before truncation check: 848 chars
[DEBUG] Registered panels: ['awakening', 'dungeons', 'profile', 'profile_v2', 'log_reps', 'buffs', 'incursions', 'skill_tree']
[DEBUG] Panel 'awakening': EnhancedAwakeningPanel
[DEBUG] Panel 'dungeons': DungeonPanel
[DEBUG] Panel 'profile': ProfilePanel
[DEBUG] Panel 'profile_v2': ProfileV2Panel
[DEBUG] Panel 'log_reps': LogRepsPanel
[DEBUG] Panel 'buffs': BuffsPanel
[DEBUG] Panel 'incursions': IncursionPanel
[DEBUG] Panel 'skill_tree': SkillTreePanel
[DEBUG] Panel options: [('Profile', 'profile'), ('Profile V2', 'profile_v2'), ('Awakening', 'awakening'), ('Skill Tree', 'skill_tree'), ('Dungeons', 'dungeons'), ('Log Reps', 'log_reps'), ('Buffs & Consumables', 'buffs'), ('Shadow Incursions', 'incursions')]
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Successfully added panel dropdown for user 168786415096692736
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Adding category dropdown for group=upper, category=10
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Using cached library data (age: 10.3s)
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Finding categories for group 'upper', expecting: ['PUSH', 'PULL', 'PULL_VERTICAL', 'UPPER_DYNAMIC', 'GRIP', 'BALLISTIC']
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Found 6 categories for group 'upper': ['PUSH', 'PULL', 'PULL_VERTICAL', 'UPPER_DYNAMIC', 'GRIP', 'BALLISTIC']
[INFO] 2025-07-30 18:07:47 [INFO] features.skills.ui.skill_tree_panel
Using cached profile data for user 168786415096692736 (age: 8.6s)
