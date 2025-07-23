# **Epic 6: Final Integration & Discord Bot**

**Goal**: Wire up all V2 backend features to the existing Discord bot UI panels.

## **Story 6.1: Update Bot API Client**

* **As a** developer, **I want** the Discord bot's API client to be updated, **so that** it can communicate with the new /v2/ endpoints.  
* **AC:**  
  1. All API calls in the bot are updated to point to the new V2 endpoints.  
  2. The client correctly handles the new data schemas and asynchronous responses.

## **Story 6.2: Build New UI Panels**

* **As a** user, **I want** to interact with all the new V2 features through the Discord bot, **so that** I have a seamless experience.  
* **AC:**  
  1. A new Profile panel is built that displays the Aura score and other V2 stats.  
  2. A new interactive Skill Tree panel is built for browsing and unlocking nodes.  
  3. New panels for the Awakening and Dungeon flows are created.  
  4. **Crucially**, all new panels must reuse the visual components (headers, footers, loading UI) from the V1 panels to ensure a consistent look and feel.