Product Requirements Document: Realm of Shadows v2.0
Solo Developer Edition - Q3 2025
This document outlines the current state and future direction of the Realm of Shadows project. Its purpose is to serve as the single source of truth for all development decisions.

1.0 Current Project Status
The project has successfully migrated to a modern, scalable API-first architecture. The foundation is stable, with a FastAPI backend handling all logic and the Discord bot acting as the primary client. However, a key gameplay loop, the Awakening Ritual, is not yet implemented.

Architectural Snapshot
Backend: FastAPI with Pydantic models.

Database: PostgreSQL with AsyncPG.

Caching: Redis for performance.

Authentication: JWT tokens for API security.

Frontend: Discord.py bot client.

The separation of concerns between the API and the bot is clean, paving the way for future expansion to web or mobile apps.

Core Feature Status
REQ-API-01: Decoupled Backend API

Status: ✅ COMPLETE

Notes: All endpoints for existing features are built, validated, and documented.

REQ-USER-01: The Operative's Profile

Status: ✅ COMPLETE

Notes: User stats (XP, Level, STR, END, TECH), profile management, and history are fully functional.

REQ-LOG-01: Rep Logging Engine

Status: ✅ COMPLETE

Notes: The core workout logging mechanism, including XP calculation and exercise library, is working as intended.

REQ-QUEST-01: Quest System Framework

Status: 🔄 PARTIAL

Notes: The framework for generating and tracking quests is in place. However, it relies on the pending Awakening system to be fully utilized by the player.

REQ-AWA-01: The Awakening Ritual

Status: ❌ PENDING

Notes: This is a critical missing piece. The core logic for the daily readiness declaration and personalized quest generation is not yet built. This is the highest priority to complete the core gameplay loop.

REQ-INC-01: Shadow Incursions

Status: ✅ COMPLETE

Notes: Dynamic world events are functional, with a background scheduler making API calls correctly.

REQ-UI-01: System Hub & UI

Status: ✅ COMPLETE

Notes: The panel-based navigation system in Discord is stable and provides a solid user experience.

2.0 Immediate Development Roadmap
The focus is on completing the core gameplay loop and then introducing repeatable content to drive long-term engagement.

🎯 Priority 1: Implement the Awakening System
Finish REQ-AWA-01. This is non-negotiable and unlocks the daily gameplay loop.

Backend: Create the API endpoints (/api/awakening/*) to handle a user's daily readiness declaration (Low/Standard/High).

Logic: Implement the tiered quest generation logic based on that declaration.

Frontend: Build the Discord UI for the user to perform their "Awakening Ritual" once per day.

🎯 Priority 2: New Feature - Shadow Labyrinths
Once the Awakening system is live, begin work on the primary repeatable content system. This feature introduces dungeons (Labyrinths) and keys (Abyssal Keys) to provide on-demand challenges and a primary source for grinding crafting materials.

3.0 New Feature PRD: Shadow Labyrinths & Keys
This section details the requirements for the "Shadow Labyrinths" feature.

REQ-LAB-01: Shadow Labyrinths & Abyssal Keys
Status: 📋 PLANNED

Feature Vision & Purpose
The Shadow Labyrinths system will provide an engaging, repeatable activity for users who have completed their daily quests. It will serve as the main driver for the in-game economy, rewarding focused effort with crafting materials and other valuable resources.

The User Flow
Acquire Keys: The user obtains Abyssal Keys from daily logins (the "Awakening"), high-tier quests, or special events.

Enter Labyrinth: The user navigates to a new [ LABYRINTHS ] panel. They select a Labyrinth type and spend one Abyssal Key to begin a run.

The Run: The UI updates to an "Active Labyrinth" state. A master timer (e.g., 30 minutes) begins. The user must complete a series of sequential objectives (Nodes) by logging specific types of exercises.

Completion/Failure:

Success: Completing all Nodes before the timer expires yields a large Completion Bonus.

Failure: If the timer expires, the run ends. The user keeps rewards from completed Nodes but forfeits the final bonus.

System Mechanics
Tiers & Unlocks: Labyrinths have tiers (1-100). A user unlocks the next tier by successfully completing the previous one and meeting a minimum stat requirement (e.g., 100 STR to unlock Tier 5).

Labyrinth Types:

Might: Focuses on PUSH/PULL exercises. Rewards STR-related materials.

Fortitude: Focuses on CORE/LEGS exercises. Rewards END-related materials.

Shadows: Focuses on difficult, form-based exercises. Rewards rare materials.

Run Instance: When a run begins, a LabyrinthRun is created in the database, tracking the user, start time, status, and objective progress.

Abyssal Keys (Economy):

Sources: +1 on Daily Awakening, potential reward from high-tier quests and Incursions.

Sink: 1 key is consumed to enter a Labyrinth. This is non-refundable.

Implementation Plan: Shadow Labyrinths (for AI Assistant)
Implement the following steps in sequence.

Step 1: Database Schema
First, update the database tables.

Task 1.1: Update users Table:

Add abyssal_keys (Integer, default 1).

Add highest_labyrinth_tier_unlocked (Integer, default 1).

Task 1.2: Create labyrinth_templates Table:

id, tier, type (String), name, timer_duration_seconds, min_stat_requirement (JSONB).

Task 1.3: Create labyrinth_template_objectives Table:

id, template_id (FK), sequence_order, description, objective_type (e.g., "perform_reps"), target_category, target_value, rewards (JSONB).

Task 1.4: Create labyrinth_runs Table:

id, user_id (FK), template_id (FK), status (String: "active", "completed", "failed"), start_time, expires_at.

Task 1.5: Create labyrinth_run_objective_progress Table:

id, run_id (FK), template_objective_id (FK), current_progress, is_completed.

Step 2: Core Logic (Services)
Create the business logic functions separate from the API routes.

Task 2.1: LabyrinthService:

get_available_labyrinths(user): Returns templates the user has unlocked.

start_labyrinth_run(user, template_id): Validates and consumes a key, creates the LabyrinthRun and its progress records.

get_active_labyrinth_run(user): Fetches the user's current active run.

Step 3: FastAPI Endpoints
Create the API routes.

Task 3.1: GET /labyrinths:

Calls get_available_labyrinths and returns the list of available templates.

Task 3.2: POST /labyrinths/enter:

Takes a template_id. Calls start_labyrinth_run and returns the new run instance.

Task 3.3: GET /labyrinths/active:

Calls get_active_labyrinth_run and returns the user's active run, if any.

Task 3.4: Modify POST /logging/log Endpoint (Critical):

This endpoint must be updated. When reps are logged:

Check for an active labyrinth run for the user.

If one exists, check if the logged exercise matches the current objective's target_category.

If it matches, update the progress.

If the objective is completed, grant the Node reward and advance to the next objective.

If it's the final objective, mark the entire run as "completed" and grant the Completion Bonus.

Step 4: System Integration
Connect the system to existing features.

Task 4.1: Modify "Awakening" Logic:

When implemented, the daily Awakening should grant +1 abyssal_keys.

Task 4.2: Background Expiration Task:

Create a scheduled task that runs every minute.

It should query for LabyrinthRun records where status is "active" and expires_at is in the past. Update their status to "failed".