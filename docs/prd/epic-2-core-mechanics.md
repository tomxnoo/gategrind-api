# **Epic 2: V2 Core Mechanics & Feature Re-implementation**

**Goal**: Build the core game engines and cleanly re-implement the proven features of the old system.

## **Story 2.1: Re-implement the XP Engine**

* **As a** system, **I want** the new V2 XP Engine built, **so that** user progression can be accurately calculated and stored.  
* **AC:**  
  1. The ProgressionService is built with a method add_xp(user_id, amount, category).  
  2. The service correctly calculates and applies XP to both global_xp and the specific stat's XP.  
  3. The service correctly calculates level-ups based on the formula: 100 * (current_level ^ 1.5).  
  4. Upon leveling up, the user is correctly awarded +1 to each of the three Stat Points.

## **Story 2.2: Re-implement Movement (Reps) Logging**

* **As a** user, **I want** to log my completed exercises, **so that** I can earn XP and track my progress.  
* **AC:**  
  1. A POST /v2/events/log-movement endpoint is created.  
  2. The endpoint accepts a movement_id and reps count.  
  3. The ProgressionService is called to calculate the total XP (reps * xp_per_rep) and apply it to the user's profile.  
  4. The API response includes the user's updated stats and new Aura score.

## **Story 2.3: Re-implement Incursions System**

* **As a** system, **I want** to randomly generate Incursion events throughout the day, **so that** users have spontaneous challenges.  
* **AC:**  
  1. An IncursionService is created to manage the logic for spawning and managing incursions.  
  2. A background scheduler is implemented to trigger the incursion generation process periodically.  
  3. When an incursion is active, a GET /v2/incursions/active endpoint returns its details.