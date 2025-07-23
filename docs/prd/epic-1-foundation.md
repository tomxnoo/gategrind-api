# **Epic 1: The Foundation (Database, Services & Content Bible)**

**Goal**: Build the new V2 database schema, seed it with the new V2 Movement Library, and implement the foundational service layer.

## **Story 1.1: Database Schema and Models**

* **As a** system, **I want** the complete V2 database schema implemented with SQLAlchemy models, **so that** all game data can be stored accurately.  
* **AC:**  
  1. All tables from the V2 Game Design Document are created as SQLAlchemy models.  
  2. A last_login field is added to the ascendants model.  
  3. An Alembic migration is created to set up the fresh V2 schema.

## **Story 1.2: Seed the "Content Bible"**

* **As a** system, **I want** the database to be pre-populated with the complete V2 Movement & Skill Tree Library, **so that** the core game content is available.  
* **AC:**  
  1. A seed script populates the database with all 18 movement categories and their full 5-level skill trees.

## **Story 1.3: Foundational Service Layer & Core API**

* **As a** developer, **I want** a standardized service layer and the core API foundation, **so that** all business logic is clean and the foundational content is verifiable.  
* **AC:**  
  1. A services directory is created with a base service class.  
  2. The MovementService is created with a method to fetch the skill tree library.  
  3. The GET /v2/movements/library endpoint is implemented and returns the entire skill tree library.