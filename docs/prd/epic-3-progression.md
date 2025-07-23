# **Epic 3: Core Progression & The Skill Tree**

**Goal**: Implement the new V2 skill tree library and the full user progression system.

## **Story 3.1: Implement Stat Milestone Progression**

* **As a** system, **I want** to reward users with Stat Points for hitting raw stat milestones, **so that** there is a dual path for progression.  
* **AC:**  
  1. The ProgressionService's add_xp method is updated to check if a stat level has crossed a milestone (100, 250, 500, etc.).  
  2. If a milestone is crossed, the user is awarded +1 of the corresponding Stat Point.

## **Story 3.2: Implement Skill Tree Unlocking**

* **As a** user, **I want** to spend my earned Stat Points to unlock new nodes on the Skill Tree, **so that** I can master new movements.  
* **AC:**  
  1. A POST /v2/progression/unlock-skill endpoint is created that accepts a node_id.  
  2. The ProgressionService verifies the user meets all three requirements: Ascendant Level, required Stat Points, and any prerequisite nodes.  
  3. If requirements are met, the Stat Points are deducted from the user's total.  
  4. A new entry is created in the user_skill_progress table.  
  5. The API response includes the user's updated Stat Point totals and new Aura score.