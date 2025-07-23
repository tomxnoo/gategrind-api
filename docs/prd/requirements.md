# **GateGrind V2 - Requirements**

## **2. Requirements**

### **2.1. Functional Requirements**

* **FR1: V2 Game Systems**: The system must implement the full V2 feature set: The Awakening (Daily Loop), The Dungeons (Endgame Loop), the full Skill Tree, and the "Aura" Power Level system.  
* **FR2: V1 Feature Re-implementation**: The core logic for Movement (Reps) Logging, the XP Engine, and random Incursions must be cleanly re-implemented within the new V2 architecture.  
* **FR3: V2 Content Bible**: The system must use the new, enhanced V2 Movement Library as the single source for all exercises and skills.  
* **FR4: Dual-Path Progression**: The new V2 XP Engine must support the dual-path system where users earn Stat Points from both Level-ups and Stat Milestones.  
* **FR5: Daily Login Reward**: The system must provide a simple daily login bonus to encourage player engagement.

### **2.2. Non-Functional Requirements**

* **NFR1: UI/UX Consistency**: All new UI panels created for V2 features must reuse the existing visual components and patterns from the V1 panels, including the universal header, sub-header, loading UI, and footer.  
* **NFR2: API-First Design**: All features must be exposed via a versioned (/v2/) RESTful API before client integration.  
* **NFR3: Performance & Asynchronicity**: The API must be highly performant (<200ms standard response) and use asynchronous responses for long-running actions.  
* **NFR4: Testability**: The codebase must have a minimum of 80% test coverage.  
* **NFR5: Observability**: The system must be integrated with Sentry for real-time error tracking.