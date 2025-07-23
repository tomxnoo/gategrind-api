# **Epic 4: The "Aura" Power Level System**

**Goal**: Implement the "Aura" system as the ultimate measure of a user's power.

## **Story 4.1: Implement Aura Calculation**

* **As a** system, **I want** to calculate and store a user's Aura score, **so that** there is a single metric for their overall power.  
* **AC:**  
  1. An aura field is added to the ascendants database model.  
  2. A calculate_and_update_aura method is created in the ProgressionService.  
  3. The method correctly applies the formula: (Level * 100) + (STR*10 + END*10 + TECH*5) + (Nodes Unlocked * 25).

## **Story 4.2: Real-Time Aura Updates**

* **As a** system, **I want** the Aura score to be updated in real-time whenever a contributing factor changes, **so that** the user gets immediate feedback.  
* **AC:**  
  1. The calculate_and_update_aura method is automatically called after any event that could change the score (e.g., add_xp, unlock_skill_node).  
  2. All API endpoints that trigger an Aura change must return the new, updated Aura score in their response payload.