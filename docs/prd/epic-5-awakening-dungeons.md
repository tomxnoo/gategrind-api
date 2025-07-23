# **Epic 5: The Awakening & Dungeon Systems**

**Goal**: Build the new V2 daily and endgame gameplay loops.

## **Story 5.1: The Awakening System**

* **As a** user, **I want** to perform a daily Awakening ritual, **so that** I can receive quests and earn Dungeon Keys.  
* **AC:**  
  1. An AwakeningService is created.  
  2. A POST /v2/awakening/generate endpoint is created that accepts a readiness_level.  
  3. The service uses the QuestGenerationService to create daily quests.  
  4. Upon completion of all quests, the user is awarded the correct number of Shadow Keys based on the readiness level.

## **Story 5.2: The Dungeon System**

* **As a** user, **I want** to use my Shadow Keys to enter challenging dungeons, **so that** I can earn exclusive rewards.  
* **AC:**  
  1. A DungeonService is created.  
  2. A POST /v2/dungeons/enter endpoint is created that consumes one Shadow Key.  
  3. The service verifies the user meets the dungeon's stat and level requirements.  
  4. The service generates trials using the QuestGenerationService, applying daily modifiers.  
  5. The API response is asynchronous to support the bot's loading UI.