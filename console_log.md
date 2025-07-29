[OK] Sentry initialized with DSN: https://a79a94e31ba80fa8835018abc3e28dfb@o45096452...
[INFO] Logfire monitoring disabled
2025-07-29 20:27:07,181 - app.core.config - INFO - Application started with environment: development
2025-07-29 20:27:07,182 - app.core.config - INFO - Debug mode: False
2025-07-29 20:27:07,182 - app.core.config - INFO - Database: localhost/ros_db
2025-07-29 20:27:07,182 - app.core.config - INFO - Redis: local
[OK] Static files mounted from /home/runner/workspace/app/static
[INFO] Starting Discord bot...
2025-07-29 20:27:07 INFO     discord.client logging in using static token
2025-07-29 20:27:07,330 - discord.client - INFO - logging in using static token
INFO:     Started server process [1270]
INFO:     Waiting for application startup.
[INFO] Starting FastAPI application...
[INFO] Initializing database connection pool...
[OK] Database connection pool created successfully.
2025-07-29 20:27:13,105 - core.redis_cache - INFO - Connected to Redis at rediss://default:AUwGAAIjcDFhZDU1MWI2NjVmMzY0ZTFjOTIzNDU1MDRmM2M3Mjc0M3AxMA@vocal-meerkat-19462.upstash.io:6379
[OK] Connected to Redis successfully.
[OK] FastAPI application startup complete.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
[OK] Database connection pool created successfully.
[INFO] Connecting to Redis...
2025-07-29 20:27:13,375 - core.redis_cache - INFO - Connected to Redis at rediss://default:AUwGAAIjcDFhZDU1MWI2NjVmMzY0ZTFjOTIzNDU1MDRmM2M3Mjc0M3AxMA@vocal-meerkat-19462.upstash.io:6379
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
2025-07-29 20:27:13 INFO     discord.gateway Shard ID 0 has connected to Gateway (Session ID: c6d64600ad109dd1c2f04592bff65b6d).
2025-07-29 20:27:13,904 - discord.gateway - INFO - Shard ID 0 has connected to Gateway (Session ID: c6d64600ad109dd1c2f04592bff65b6d).
════════════════════════════════════════════════════════════
🌒 The System#1314 online • ID 1386656478877716601
Guilds: 1  •  Cogs: 12
════════════════════════════════════════════════════════════
INFO:     127.0.0.1:54052 - "GET /api/v2/auth/health HTTP/1.1" 200 OK
2025-07-29 20:27:15,968 - httpx - INFO - HTTP Request: GET http://localhost:5000/api/v2/auth/health "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/auth/health
[OK] API Health Check: healthy - RoS-TRAE V2 API v2.0.0
[INFO] API Base URL: http://localhost:5000/api
[INFO] Development Mode: False
[OK] System Hub persistent view added
INFO:     172.31.88.226:52584 - "GET / HTTP/1.1" 200 OK
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
2025-07-29 20:27:16,012 - app.api.v2.dependencies.auth - INFO - DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
2025-07-29 20:27:16,017 - app.api.v2.dependencies.auth - INFO - DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
INFO:     172.31.88.226:52594 - "GET /api/v2/profiles/me HTTP/1.1" 401 Unauthorized
INFO:     172.31.88.226:52594 - "GET / HTTP/1.1" 200 OK
2025-07-29 20:27:17,372 - features.incursions.logic.scheduler - INFO - Loaded scheduler settings: testing_mode=True, auto_start=False, announcement_channel=1390756464250847353
[API_CLIENT] Returning existing singleton instance for APIClient
[API_CLIENT] User 168786415096692736 not in registered cache, ensuring registration
[DEBUG] Edited ephemeral login embed with 1 dots at 0.00 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 0.74 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 1.50 seconds
[DEBUG] Edited ephemeral login embed with 1 dots at 2.32 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 3.06 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 3.69 seconds
[DEBUG] Edited ephemeral login embed with 1 dots at 4.38 seconds
INFO:     127.0.0.1:54066 - "POST /api/v2/auth/login HTTP/1.1" 200 OK
2025-07-29 20:27:28,145 - httpx - INFO - HTTP Request: POST http://localhost:5000/api/v2/auth/login "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/auth/login
[API_CLIENT] User aqpq logged in successfully
[API_CLIENT] Attempting login for registered user 168786415096692736
[DEBUG] Edited ephemeral login embed with 2 dots at 5.10 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 5.96 seconds
INFO:     127.0.0.1:38304 - "POST /api/v2/auth/login HTTP/1.1" 200 OK
2025-07-29 20:27:29,853 - httpx - INFO - HTTP Request: POST http://localhost:5000/api/v2/auth/login "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/auth/login
[API_CLIENT] Successfully obtained token from login for user 168786415096692736
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
2025-07-29 20:27:29,876 - app.api.v2.dependencies.auth - INFO - DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
2025-07-29 20:27:29,876 - app.api.v2.dependencies.auth - INFO - DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
[DEBUG] Edited ephemeral login embed with 1 dots at 6.70 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 7.47 seconds
INFO:     127.0.0.1:38316 - "GET /api/v2/profiles/me HTTP/1.1" 500 Internal Server Error
2025-07-29 20:27:31,462 - httpx - INFO - HTTP Request: GET http://localhost:5000/api/v2/profiles/me "HTTP/1.1 500 Internal Server Error"
[API_CLIENT] HTTP Error 500: {"detail":"Failed to retrieve profile: 'Ascendant' object has no attribute 'strength_skill_points'"}
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
2025-07-29 20:27:31,465 - features.skills.ui.skill_tree_panel - INFO - Fetching fresh library data...
[API_CLIENT] Returning existing singleton instance for APIClient
[API_CLIENT] Using cached valid token for user 168786415096692736
2025-07-29 20:27:31,493 - app.api.v2.movements - INFO - Fetching complete skill tree library
[DEBUG] Edited ephemeral login embed with 3 dots at 8.15 seconds
[DEBUG] Edited ephemeral login embed with 1 dots at 8.99 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 9.67 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 10.37 seconds
[DEBUG] Edited ephemeral login embed with 1 dots at 11.14 seconds
2025-07-29 20:27:34,824 - MovementService - INFO - Successfully fetched skill tree library with 39 categories
2025-07-29 20:27:34,825 - app.api.v2.movements - INFO - Successfully returned skill tree library with 39 categories
INFO:     127.0.0.1:38324 - "GET /api/v2/movements/library HTTP/1.1" 200 OK
2025-07-29 20:27:34,937 - httpx - INFO - HTTP Request: GET http://localhost:5000/api/v2/movements/library "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/movements/library
2025-07-29 20:27:34,939 - features.skills.ui.skill_tree_panel - INFO - Fetching fresh profile data for user 168786415096692736...
[API_CLIENT] Returning existing singleton instance for APIClient
[API_CLIENT] Using cached valid token for user 168786415096692736
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
2025-07-29 20:27:34,960 - app.api.v2.dependencies.auth - INFO - DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
2025-07-29 20:27:34,961 - app.api.v2.dependencies.auth - INFO - DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
[DEBUG] Edited ephemeral login embed with 2 dots at 11.83 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 12.49 seconds
[DEBUG] Edited ephemeral login embed with 1 dots at 13.13 seconds
INFO:     127.0.0.1:38334 - "GET /api/v2/profiles/me HTTP/1.1" 500 Internal Server Error
2025-07-29 20:27:36,532 - httpx - INFO - HTTP Request: GET http://localhost:5000/api/v2/profiles/me "HTTP/1.1 500 Internal Server Error"
[API_CLIENT] HTTP Error 500: {"detail":"Failed to retrieve profile: 'Ascendant' object has no attribute 'strength_skill_points'"}
2025-07-29 20:27:36,533 - features.skills.ui.skill_tree_panel - ERROR - Failed to fetch profile data for user 168786415096692736: HTTP 500: Failed to retrieve profile: 'Ascendant' object has no attribute 'strength_skill_points'
2025-07-29 20:27:36,536 - features.skills.ui.skill_tree_panel - INFO - Clearing auth cache for user 168786415096692736 and retrying...
[API_CLIENT] Cleared auth cache for user 168786415096692736
[API_CLIENT] User 168786415096692736 not in registered cache, ensuring registration
[DEBUG] Edited ephemeral login embed with 2 dots at 13.85 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 14.61 seconds
[DEBUG] Edited ephemeral login embed with 1 dots at 15.33 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 16.06 seconds
[DEBUG] Edited ephemeral login embed with 3 dots at 16.78 seconds
INFO:     127.0.0.1:54530 - "POST /api/v2/auth/login HTTP/1.1" 200 OK
2025-07-29 20:27:40,153 - httpx - INFO - HTTP Request: POST http://localhost:5000/api/v2/auth/login "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/auth/login
[API_CLIENT] User aqpq logged in successfully
[API_CLIENT] Attempting login for registered user 168786415096692736
[DEBUG] Edited ephemeral login embed with 1 dots at 17.44 seconds
[DEBUG] Edited ephemeral login embed with 2 dots at 18.07 seconds
INFO:     127.0.0.1:54546 - "POST /api/v2/auth/login HTTP/1.1" 200 OK
2025-07-29 20:27:41,746 - httpx - INFO - HTTP Request: POST http://localhost:5000/api/v2/auth/login "HTTP/1.1 200 OK"
[API_CLIENT] Successfully called V2 endpoint: /v2/auth/login
[API_CLIENT] Successfully obtained token from login for user 168786415096692736
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
2025-07-29 20:27:41,771 - app.api.v2.dependencies.auth - INFO - DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
2025-07-29 20:27:41,771 - app.api.v2.dependencies.auth - INFO - DEBUG V2 AUTH: DEV_MODE env var: 'false', is_development_mode: False
[DEBUG] Edited ephemeral login embed with 3 dots at 18.83 seconds
INFO:     127.0.0.1:54560 - "GET /api/v2/profiles/me HTTP/1.1" 500 Internal Server Error
2025-07-29 20:27:43,484 - httpx - INFO - HTTP Request: GET http://localhost:5000/api/v2/profiles/me "HTTP/1.1 500 Internal Server Error"
[API_CLIENT] HTTP Error 500: {"detail":"Failed to retrieve profile: 'Ascendant' object has no attribute 'strength_skill_points'"}
2025-07-29 20:27:43,485 - features.skills.ui.skill_tree_panel - ERROR - Profile retry also failed for user 168786415096692736: HTTP 500: Failed to retrieve profile: 'Ascendant' object has no attribute 'strength_skill_points'
[DEBUG] Pre-caching failed: HTTP 500: Failed to retrieve profile: 'Ascendant' object has no attribute 'strength_skill_points'
[DEBUG] Edited ephemeral login embed with 1 dots at 19.50 seconds
