# **GateGrind V2 \- Final Consolidated PRD**

Version: 2.1 (Definitive)  
Date: 2025-07-24  
Author: John, BMad Product Manager

## **1\. Introduction & Project Vision**

### **1.1. Project Overview**

This document outlines the Product Requirements for the **GateGrind V2** backend. This project is a hybrid, best described as **"Brownfield x Greenfield \= V2"**.

* **Greenfield**: We will build the new V2 game systems (Awakening, Dungeons, Aura, Skill Tree) from the ground up on a clean, modern architecture.  
* **Brownfield**: We will re-implement the best, proven features from the existing V1 system (Movement Logging, XP Engine, Incursions) into the new V2 architecture, ensuring their logic is preserved and enhanced.

The primary goal is to create a single, authoritative API that serves as the "source of truth" for all game mechanics. This API will integrate seamlessly with the existing, high-quality Python Discord bot UI and future applications like webapp and mobile app.

### **1.2. Core Product Goals**

* **Build a True RPG Fitness Experience**: Create an engaging game with deep progression, strategic choices, and rewarding gameplay loops.  
* **Preserve the "Living Nexus" UI**: The backend must fully support and enhance the existing ephemeral, panel-based Discord UI.  
* **Establish a Scalable Foundation**: Create a clean, modular, and well-tested codebase for future growth.  
* **Unify Progression**: Implement the "Aura" system as a single, compelling metric of a user's total power.

## **2\. Requirements**

### **2.1. Functional Requirements**

* **FR1: V2 Game Systems**: The system must implement the full V2 feature set: The Awakening (Daily Loop), The Dungeons (Endgame Loop), the full Skill Tree, and the "Aura" Power Level system.  
* **FR2: V1 Feature Re-implementation**: The core logic for Movement (Reps) Logging, the XP Engine, and random Incursions must be cleanly re-implemented within the new V2 architecture.  
* **FR3: V2 Content Bible**: The system must use the new, enhanced V2 Movement Library as the single source for all exercises and skills.  
* **FR4: Dual-Path Progression**: The new V2 XP Engine must support the dual-path system where users earn Stat Points from both Level-ups and Stat Milestones.  
* **FR5: Daily Login Reward**: The system must provide a simple daily login bonus to encourage player engagement.

### **2.2. Non-Functional Requirements**

* **NFR1: UI/UX Consistency**: All new UI panels created for V2 features must reuse the existing visual components and patterns from the V1 panels, including the universal header, sub-header, loading UI, and footer.  
* **NFR2: API-First Design**: All features must be exposed via a versioned (/v2/) RESTful API before client integration.  
* **NFR3: Performance & Asynchronicity**: The API must be highly performant (\<200ms standard response) and use asynchronous responses for long-running actions.  
* **NFR4: Testability**: The codebase must have a minimum of 80% test coverage.  
* **NFR5: Observability**: The system must be integrated with Sentry for real-time error tracking.

## **3\. Epic & Story Structure**

The project is divided into six sequential epics.

* **Epic 1: The Foundation (Database, Services & Content Bible)**  
* **Epic 2: V2 Core Mechanics & Feature Re-implementation**  
* **Epic 3: Core Progression & The Skill Tree**  
* **Epic 4: The "Aura" Power Level System**  
* **Epic 5: The Awakening & Dungeon Systems**  
* **Epic 6: Final Integration & Discord Bot**

## **Epic 1: The Foundation (Database, Services & Content Bible)**

**Goal**: Build the new V2 database schema, seed it with the new V2 Movement Library, and implement the foundational service layer.

### **Story 1.1: Database Schema and Models**

* **As a** system, **I want** the complete V2 database schema implemented with SQLAlchemy models, **so that** all game data can be stored accurately.  
* **AC:**  
  1. All tables from the V2 Game Design Document are created as SQLAlchemy models.  
  2. A last\_login field is added to the ascendants model.  
  3. An Alembic migration is created to set up the fresh V2 schema.

### **Story 1.2: Seed the "Content Bible"**

* **As a** system, **I want** the database to be pre-populated with the complete V2 Movement & Skill Tree Library, **so that** the core game content is available.  
* **AC:**  
  1. A seed script populates the database with all 18 movement categories and their full 5-level skill trees.

### **Story 1.3: Foundational Service Layer & Core API**

* **As a** developer, **I want** a standardized service layer and the core API foundation, **so that** all business logic is clean and the foundational content is verifiable.  
* **AC:**  
  1. A services directory is created with a base service class.  
  2. The MovementService is created with a method to fetch the skill tree library.  
  3. The GET /v2/movements/library endpoint is implemented and returns the entire skill tree library.

## **Epic 2: V2 Core Mechanics & Feature Re-implementation**

**Goal**: Build the core game engines and cleanly re-implement the proven features of the old system.

### **Story 2.1: Re-implement the XP Engine**

* **As a** system, **I want** the new V2 XP Engine built, **so that** user progression can be accurately calculated and stored.  
* **AC:**  
  1. The ProgressionService is built with a method add\_xp(user\_id, amount, category).  
  2. The service correctly calculates and applies XP to both global\_xp and the specific stat's XP.  
  3. The service correctly calculates level-ups based on the formula: 100 \* (current\_level ^ 1.5).  
  4. Upon leveling up, the user is correctly awarded \+1 to each of the three Stat Points.

### **Story 2.2: Re-implement Movement (Reps) Logging**

* **As a** user, **I want** to log my completed exercises, **so that** I can earn XP and track my progress.  
* **AC:**  
  1. A POST /v2/events/log-movement endpoint is created.  
  2. The endpoint accepts a movement\_id and reps count.  
  3. The ProgressionService is called to calculate the total XP (reps \* xp\_per\_rep) and apply it to the user's profile.  
  4. The API response includes the user's updated stats and new Aura score.

### **Story 2.3: Re-implement Incursions System**

* **As a** system, **I want** to randomly generate Incursion events throughout the day, **so that** users have spontaneous challenges.  
* **AC:**  
  1. An IncursionService is created to manage the logic for spawning and managing incursions.  
  2. A background scheduler is implemented to trigger the incursion generation process periodically.  
  3. When an incursion is active, a GET /v2/incursions/active endpoint returns its details.

## **Epic 3: Core Progression & The Skill Tree**

**Goal**: Implement the new V2 skill tree library and the full user progression system.

### **Story 3.1: Implement Stat Milestone Progression**

* **As a** system, **I want** to reward users with Stat Points for hitting raw stat milestones, **so that** there is a dual path for progression.  
* **AC:**  
  1. The ProgressionService's add\_xp method is updated to check if a stat level has crossed a milestone (100, 250, 500, etc.).  
  2. If a milestone is crossed, the user is awarded \+1 of the corresponding Stat Point.

### **Story 3.2: Implement Skill Tree Unlocking**

* **As a** user, **I want** to spend my earned Stat Points to unlock new nodes on the Skill Tree, **so that** I can master new movements.  
* **AC:**  
  1. A POST /v2/progression/unlock-skill endpoint is created that accepts a node\_id.  
  2. The ProgressionService verifies the user meets all three requirements: Ascendant Level, required Stat Points, and any prerequisite nodes.  
  3. If requirements are met, the Stat Points are deducted from the user's total.  
  4. A new entry is created in the user\_skill\_progress table.  
  5. The API response includes the user's updated Stat Point totals and new Aura score.

## **Epic 4: The "Aura" Power Level System**

**Goal**: Implement the "Aura" system as the ultimate measure of a user's power.

### **Story 4.1: Implement Aura Calculation**

* **As a** system, **I want** to calculate and store a user's Aura score, **so that** there is a single metric for their overall power.  
* **AC:**  
  1. An aura field is added to the ascendants database model.  
  2. A calculate\_and\_update\_aura method is created in the ProgressionService.  
  3. The method correctly applies the formula: (Level \* 100\) \+ (STR\*10 \+ END\*10 \+ TECH\*5) \+ (Nodes Unlocked \* 25).

### **Story 4.2: Real-Time Aura Updates**

* **As a** system, **I want** the Aura score to be updated in real-time whenever a contributing factor changes, **so that** the user gets immediate feedback.  
* **AC:**  
  1. The calculate\_and\_update\_aura method is automatically called after any event that could change the score (e.g., add\_xp, unlock\_skill\_node).  
  2. All API endpoints that trigger an Aura change must return the new, updated Aura score in their response payload.

## **Epic 5: The Awakening & Dungeon Systems**

**Goal**: Build the new V2 daily and endgame gameplay loops.

### **Story 5.1: The Awakening System**

* **As a** user, **I want** to perform a daily Awakening ritual, **so that** I can receive quests and earn Dungeon Keys.  
* **AC:**  
  1. An AwakeningService is created.  
  2. A POST /v2/awakening/generate endpoint is created that accepts a readiness\_level.  
  3. The service uses the QuestGenerationService to create daily quests.  
  4. Upon completion of all quests, the user is awarded the correct number of Shadow Keys based on the readiness level.

### **Story 5.2: The Dungeon System**

* **As a** user, **I want** to use my Shadow Keys to enter challenging dungeons, **so that** I can earn exclusive rewards.  
* **AC:**  
  1. A DungeonService is created.  
  2. A POST /v2/dungeons/enter endpoint is created that consumes one Shadow Key.  
  3. The service verifies the user meets the dungeon's stat and level requirements.  
  4. The service generates trials using the QuestGenerationService, applying daily modifiers.  
  5. The API response is asynchronous to support the bot's loading UI.

## **Epic 6: Final Integration & Discord Bot**

**Goal**: Wire up all V2 backend features to the existing Discord bot UI panels.

### **Story 6.1: Update Bot API Client**

* **As a** developer, **I want** the Discord bot's API client to be updated, **so that** it can communicate with the new /v2/ endpoints.  
* **AC:**  
  1. All API calls in the bot are updated to point to the new V2 endpoints.  
  2. The client correctly handles the new data schemas and asynchronous responses.

### **Story 6.2: Build New UI Panels**

* **As a** user, **I want** to interact with all the new V2 features through the Discord bot, **so that** I have a seamless experience.  
* **AC:**  
  1. A new Profile panel is built that displays the Aura score and other V2 stats.  
  2. A new interactive Skill Tree panel is built for browsing and unlocking nodes.  
  3. New panels for the Awakening and Dungeon flows are created.  
  4. **Crucially**, all new panels must reuse the visual components (headers, footers, loading UI) from the V1 panels to ensure a consistent look and feel.