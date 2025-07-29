[OK] Sentry initialized with DSN: https://a79a94e31ba80fa8835018abc3e28dfb@o45096452...
[INFO] Logfire monitoring disabled
2025-07-29 16:53:40,580 - app.core.config - INFO - Application started with environment: development
2025-07-29 16:53:40,581 - app.core.config - INFO - Debug mode: False
2025-07-29 16:53:40,581 - app.core.config - INFO - Database: localhost/ros_db
2025-07-29 16:53:40,581 - app.core.config - INFO - Redis: local
[OK] Static files mounted from /home/runner/workspace/app/static
[INFO] Starting Discord bot...
2025-07-29 16:53:40 INFO     discord.client logging in using static token
2025-07-29 16:53:40,758 - discord.client - INFO - logging in using static token
INFO:     Started server process [3837]
INFO:     Waiting for application startup.
[INFO] Starting FastAPI application...
[INFO] Initializing database connection pool...
[OK] Database connection pool created successfully.
2025-07-29 16:53:42,723 - core.redis_cache - INFO - Connected to Redis at rediss://default:AUwGAAIjcDFhZDU1MWI2NjVmMzY0ZTFjOTIzNDU1MDRmM2M3Mjc0M3AxMA@vocal-meerkat-19462.upstash.io:6379
[OK] Connected to Redis successfully.
[OK] FastAPI application startup complete.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
[OK] Database connection pool created successfully.
[INFO] Connecting to Redis...
2025-07-29 16:53:42,756 - core.redis_cache - INFO - Connected to Redis at rediss://default:AUwGAAIjcDFhZDU1MWI2NjVmMzY0ZTFjOTIzNDU1MDRmM2M3Mjc0M3AxMA@vocal-meerkat-19462.upstash.io:6379
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
INFO:     172.31.96.98:52174 - "GET / HTTP/1.1" 200 OK
INFO:     172.31.96.98:52174 - "GET / HTTP/1.1" 200 OK
2025-07-29 16:53:50 INFO     discord.gateway Shard ID 0 has connected to Gateway (Session ID: 6c8a46465abb60a7d8c0a8ed0ea4e389).
2025-07-29 16:53:50,732 - discord.gateway - INFO - Shard ID 0 has connected to Gateway (Session ID: 6c8a46465abb60a7d8c0a8ed0ea4e389).
════════════════════════════════════════════════════════════
🌒 The System#1314 online • ID 1386656478877716601
Guilds: 1  •  Cogs: 12
════════════════════════════════════════════════════════════
INFO:     127.0.0.1:53584 - "GET /api/v2/auth/health HTTP/1.1" 200 OK
2025-07-29 16:53:52,844 - httpx - INFO - HTTP Request: GET http://localhost:5000/api/v2/auth/health "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/auth/health
[OK] API Health Check: healthy - RoS-TRAE V2 API v2.0.0
[INFO] API Base URL: http://localhost:5000/api
[INFO] Development Mode: False
[OK] System Hub persistent view added
2025-07-29 16:53:54,273 - features.incursions.logic.scheduler - INFO - Loaded scheduler settings: testing_mode=True, auto_start=False, announcement_channel=1390756464250847353
[API_CLIENT] Returning existing singleton instance for APIClient
[DEBUG] Edited ephemeral login embed with 1 dots at 0.00 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 0.71 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 1.51 seconds
[DEBUG] Edited ephemeral login embed with 1 dots at 3.30 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 4.11 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 4.99 seconds
INFO:     127.0.0.1:42702 - "POST /api/v2/auth/login HTTP/1.1" 200 OK
2025-07-29 16:54:02,419 - httpx - INFO - HTTP Request: POST http://localhost:5000/api/v2/auth/login "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/auth/login
[API_CLIENT] User aqpq logged in successfully
[DEBUG] Edited ephemeral login embed with 1 dots at 5.62 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 6.34 seconds
INFO:     127.0.0.1:42708 - "POST /api/v2/auth/login HTTP/1.1" 200 OK
2025-07-29 16:54:04,176 - httpx - INFO - HTTP Request: POST http://localhost:5000/api/v2/auth/login "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/auth/login
[DEBUG] Edited ephemeral login embed with 3 dots at 7.08 seconds
[DEBUG] Edited ephemeral login embed with 1 dots at 7.76 seconds
INFO:     127.0.0.1:42712 - "GET /api/v2/profiles/me HTTP/1.1" 200 OK
2025-07-29 16:54:05,959 - httpx - INFO - HTTP Request: GET http://localhost:5000/api/v2/profiles/me "HTTP/1.1 200 OK"
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
2025-07-29 16:54:05,961 - features.skills.ui.skill_tree_panel - INFO - Fetching fresh library data...
[API_CLIENT] Returning existing singleton instance for APIClient
2025-07-29 16:54:05,990 - app.api.v2.movements - INFO - Fetching complete skill tree library
[DEBUG] Edited ephemeral login embed with 2 dots at 8.49 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 9.31 seconds
[DEBUG] Edited ephemeral login embed with 1 dots at 10.00 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 10.79 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 11.70 seconds
2025-07-29 16:54:09,396 - MovementService - INFO - Successfully fetched skill tree library with 39 categories
2025-07-29 16:54:09,397 - app.api.v2.movements - INFO - Successfully returned skill tree library with 39 categories
INFO:     127.0.0.1:42766 - "GET /api/v2/movements/library HTTP/1.1" 200 OK
2025-07-29 16:54:09,510 - httpx - INFO - HTTP Request: GET http://localhost:5000/api/v2/movements/library "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/movements/library
2025-07-29 16:54:09,513 - features.skills.ui.skill_tree_panel - INFO - Fetching fresh profile data for user 168786415096692736...
[API_CLIENT] Returning existing singleton instance for APIClient
[DEBUG] Edited ephemeral login embed with 1 dots at 12.38 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 13.01 seconds
INFO:     127.0.0.1:52702 - "GET /api/v2/profiles/me HTTP/1.1" 200 OK
2025-07-29 16:54:11,111 - httpx - INFO - HTTP Request: GET http://localhost:5000/api/v2/profiles/me "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/profiles/me
[DEBUG] Edited ephemeral login embed with 3 dots at 13.75 seconds
2025-07-29 16:54:15,859 - features.skills.ui.skill_tree_panel - INFO - Using cached library data (age: 6.3s)
2025-07-29 16:54:15,859 - features.skills.ui.skill_tree_panel - INFO - Using cached profile data for user 168786415096692736 (age: 4.7s)
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
[DEBUG] Edited loading embed with 1 dots at 0.00 seconds
[DEBUG] Edited loading embed with 2 dots at 0.51 seconds
[DEBUG] Edited loading embed with 3 dots at 1.13 seconds
[DEBUG] Animation loop completed after 1.77 seconds
2025-07-29 16:54:24,322 - features.skills.ui.skill_tree_panel - INFO - Using cached library data (age: 14.8s)
2025-07-29 16:54:24,322 - features.skills.ui.skill_tree_panel - INFO - Using cached library data (age: 14.8s)
2025-07-29 16:54:24,323 - features.skills.ui.skill_tree_panel - INFO - Using cached profile data for user 168786415096692736 (age: 13.2s)
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
2025-07-29 16:54:24,323 - features.skills.ui.skill_tree_panel - INFO - Using cached profile data for user 168786415096692736 (age: 13.2s)
[DEBUG] Edited loading embed with 1 dots at 0.00 seconds
[DEBUG] Edited loading embed with 2 dots at 0.55 seconds
[DEBUG] Edited loading embed with 3 dots at 1.04 seconds
[DEBUG] Animation loop completed after 1.72 seconds
2025-07-29 16:54:31,295 - features.skills.ui.skill_tree_panel - INFO - Using cached library data (age: 21.8s)
2025-07-29 16:54:31,295 - features.skills.ui.skill_tree_panel - INFO - Using cached library data (age: 21.8s)
2025-07-29 16:54:31,295 - features.skills.ui.skill_tree_panel - INFO - Using cached profile data for user 168786415096692736 (age: 20.2s)
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
[DEBUG] Edited loading embed with 1 dots at 0.00 seconds
[DEBUG] Edited loading embed with 2 dots at 0.66 seconds
[DEBUG] Edited loading embed with 3 dots at 1.26 seconds
[DEBUG] Animation loop completed after 1.83 seconds
