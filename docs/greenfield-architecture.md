# **GateGrind V2 \- Final Consolidated Architecture**

Version: 2.1 (Definitive)  
Date: 2025-07-24  
Author: Winston, BMad Architect

## **1\. Introduction**

This document provides the complete technical architecture for the **GateGrind V2** backend. It is the direct technical translation of the approved GateGrind V2 \- Definitive PRD and the GateGrind Backend Architecture & Game Design Document (V2.1). This document supersedes all previous versions and serves as the single source of truth for all technical implementation.

The architecture is designed for a **"Brownfield x Greenfield \= V2"** project, supporting a full greenfield implementation of all V2 game systems while enabling a clean, safe re-implementation of proven V1 features.

| Date | Version | Description | Author |
| :---- | :---- | :---- | :---- |
| 2025-07-24 | 2.1 | Consolidated detailed architecture with final team enhancements. | Winston |

## **2\. High-Level Architecture**

The system will be built using a **Hexagonal (Ports and Adapters)** architecture. This pattern isolates the core application and domain logic from external concerns, ensuring the business logic is pure, highly testable, and independent of its delivery mechanism.

### **2.1. System Diagram**

graph TD  
    subgraph "Clients (External)"  
        A\[Python Discord Bot\]  
        B\[Future Web App\]  
    end

    subgraph "GateGrind V2 API (FastAPI Application)"  
        C\[API Layer / Controllers \<br\>\<i\>(HTTP Port)\</i\>\]  
        D\[Application / Service Layer \<br\>\<i\>(Core Logic)\</i\>\]  
        E\[Domain Layer \<br\>\<i\>(Entities & Rules)\</i\>\]  
        F\[Infrastructure Layer \<br\>\<i\>(Adapters)\</i\>\]  
    end

    subgraph "Infrastructure (External)"  
        G\[NeonDB (PostgreSQL)\]  
        H\[Redis Cache\]  
        I\[Sentry (Monitoring)\]  
        J\[External APIs, e.g., Discord\]  
    end

    A \--\> C  
    B \--\> C  
    C \--\> D  
    D \--\> E  
    D \--\> F  
    F \--\> G  
    F \--\> H  
    D \-- Reports Errors \--\> I  
    F \--\> J

### **2.2. Component Responsibilities**

* **API Layer (Controllers)**: The entry point for all external requests. Responsible for parsing and validating incoming data (via Pydantic), invoking the appropriate application service, and formatting the response.  
* **Application Layer (Services)**: Orchestrates the application's use cases. It contains no business logic itself but coordinates domain objects and infrastructure adapters to perform tasks. This is where transactions, caching logic, and error reporting to Sentry will be handled.  
* **Domain Layer (Entities & Rules)**: The heart of the application. Contains the core business entities (e.g., Ascendant, SkillTreeNode) and the rules that govern them. This layer has zero dependencies on any external framework or tool.  
* **Infrastructure Layer (Adapters)**: The implementation of external-facing concerns. This includes database repositories that interact with NeonDB, a cache client for Redis, and clients for any other external APIs.

## **3\. Technology Stack**

This is the definitive technology stack for the project. All development must adhere to these choices.

| Category | Technology | Version | Purpose & Rationale |
| :---- | :---- | :---- | :---- |
| **Runtime** | Python | 3.11+ | Modern, stable, and performant Python version. |
| **Framework** | FastAPI | Latest | High-performance API framework with automatic validation and docs. |
| **Database** | NeonDB (PostgreSQL) | 16.x | Serverless, scalable PostgreSQL for the primary data store. |
| **ORM** | SQLAlchemy | 2.0+ | The industry-standard ORM for Python, providing robust data access. |
| **Data Models** | Pydantic | 2.x | Core to FastAPI for data validation, settings, and API schemas. |
| **Caching** | Redis | 7.x | High-performance in-memory cache for the skill tree and other hot data. |
| **Testing** | Pytest | Latest | Powerful and flexible testing framework for Python. |
| **Linting/Formatting** | Ruff & Black | Latest | Fast, comprehensive linting and opinionated code formatting. |
| **Monitoring** | Sentry | Latest | Real-time error tracking and performance monitoring. |
| **CI/CD** | GitHub Actions | N/A | Automate testing, linting, and future deployments. |

## **4\. Architectural Enhancements (from Team Review)**

The following enhancements are integrated into the architecture to improve UI/UX and engagement:

* **Profile Panel DTO**: The GET /v2/users/me/profile endpoint will return a single, comprehensive data object optimized for rendering the main Discord UI panel, minimizing API calls and latency.  
* **Asynchronous API Responses**: For potentially long-running actions (/v2/dungeons/enter), the API will immediately return a 202 Accepted response and process the request in a background task. This allows the Discord UI to remain responsive.  
* **Daily Login Service**: A new service will manage a daily login reward, supported by a last\_login field in the ascendants database model.  
* **Real-Time Aura Feedback**: All API endpoints that modify a user's progression (e.g., completing a quest) **must** return the new, updated Aura score in the response payload to provide immediate feedback to the user.

## **5\. Database Schema**

The schema will be implemented using SQLAlchemy models. This provides a Python-native way to define tables and relationships.

\# A conceptual representation of the SQLAlchemy models

import datetime  
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum  
from sqlalchemy.orm import relationship, declarative\_base

Base \= declarative\_base()

class Ascendant(Base):  
    \_\_tablename\_\_ \= 'ascendants'  
    id \= Column(Integer, primary\_key=True)  
    discord\_id \= Column(String, unique=True, index=True, nullable=False)  
    username \= Column(String)  
    level \= Column(Integer, default=1)  
    global\_xp \= Column(Integer, default=0)  
    strength\_points \= Column(Integer, default=0)  
    endurance\_points \= Column(Integer, default=0)  
    technique\_points \= Column(Integer, default=0)  
    rested\_xp\_pool \= Column(Integer, default=0)  
    aura \= Column(Integer, default=0, index=True)  
    last\_login \= Column(DateTime, default=datetime.datetime.utcnow) \# For daily login  
    created\_at \= Column(DateTime, default=datetime.datetime.utcnow)  
    updated\_at \= Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Stat(Base):  
    \_\_tablename\_\_ \= 'stats'  
    id \= Column(Integer, primary\_key=True)  
    ascendant\_id \= Column(Integer, ForeignKey('ascendants.id'))  
    str\_level \= Column(Integer, default=1)  
    str\_xp \= Column(Integer, default=0)  
    end\_level \= Column(Integer, default=1)  
    end\_xp \= Column(Integer, default=0)  
    tech\_level \= Column(Integer, default=1)  
    tech\_xp \= Column(Integer, default=0)

class MovementCategory(Base):  
    \_\_tablename\_\_ \= 'movement\_categories'  
    id \= Column(String, primary\_key=True)  
    name \= Column(String, nullable=False)  
    description \= Column(String)

class SkillTreeNode(Base):  
    \_\_tablename\_\_ \= 'skill\_tree\_nodes'  
    id \= Column(Integer, primary\_key=True)  
    category\_id \= Column(String, ForeignKey('movement\_categories.id'))  
    level \= Column(Integer, nullable=False)  
    name \= Column(String, nullable=False)  
    description \= Column(String)  
    required\_ascendant\_level \= Column(Integer, default=1)  
    required\_str\_points \= Column(Integer, default=0)  
    required\_end\_points \= Column(Integer, default=0)  
    required\_tech\_points \= Column(Integer, default=0)

class Movement(Base):  
    \_\_tablename\_\_ \= 'movements'  
    id \= Column(Integer, primary\_key=True)  
    node\_id \= Column(Integer, ForeignKey('skill\_tree\_nodes.id'))  
    name \= Column(String, nullable=False)  
    xp\_per\_rep \= Column(Integer, default=1)

class UserSkillProgress(Base):  
    \_\_tablename\_\_ \= 'user\_skill\_progress'  
    ascendant\_id \= Column(Integer, ForeignKey('ascendants.id'), primary\_key=True)  
    node\_id \= Column(Integer, ForeignKey('skill\_tree\_nodes.id'), primary\_key=True)  
    unlocked\_at \= Column(DateTime, default=datetime.datetime.utcnow)

class Quest(Base):  
    \_\_tablename\_\_ \= 'quests'  
    id \= Column(Integer, primary\_key=True)  
    ascendant\_id \= Column(Integer, ForeignKey('ascendants.id'))  
    title \= Column(String)  
    description \= Column(String)  
    source \= Column(String) \# 'Awakening', 'Dungeon', 'Incursion'  
    status \= Column(String, default='active') \# 'active', 'completed'

class DungeonKey(Base):  
    \_\_tablename\_\_ \= 'dungeon\_keys'  
    id \= Column(Integer, primary\_key=True)  
    ascendant\_id \= Column(Integer, ForeignKey('ascendants.id'))  
    key\_type \= Column(String, default='shadow\_key')  
    quantity \= Column(Integer, default=0)

class DungeonProgress(Base):  
    \_\_tablename\_\_ \= 'dungeon\_progress'  
    id \= Column(Integer, primary\_key=True)  
    ascendant\_id \= Column(Integer, ForeignKey('ascendants.id'))  
    highest\_level\_completed \= Column(Integer, default=0)

## **6\. Core Services Design**

### **6.1. V2 Services & V1 Re-implementation**

* **V2 Greenfield Services**: New services (DungeonService, AwakeningService, DailyLoginService) will be built from scratch following the Hexagonal architecture.  
* **V1 Brownfield Re-implementation**: The logic for Movement Logging, the XP Engine, and Incursions will be cleanly re-implemented within the new V2 service structure (ProgressionService, IncursionService). They will be treated as new features but will use the existing V1 code as a definitive logical reference.

### **6.2. ProgressionService**

This service will be the central hub for all user progression.

* add\_xp(user\_id, amount, category): Adds XP, checks for Ascendant level-ups, and checks for Stat Milestone rewards.  
* unlock\_skill\_node(user\_id, node\_id): Verifies all requirements (level, points, etc.), consumes points, and updates user progress.  
* calculate\_and\_update\_aura(user\_id):  
  * **Trigger**: This method will be called *internally* by the service whenever a contributing factor changes (level up, stat increase, skill unlock).  
  * **Logic**: It will fetch the user's complete profile, apply the Aura formula, and save the new value to the ascendants table.  
  * **Performance**: This on-write calculation ensures that reading a user's profile is always fast, as the Aura score is pre-calculated.

### **6.3. QuestGenerationService**

This is the universal quest engine.

* generate\_quests(user, config: QuestConfig): A single, powerful method that takes a configuration object to generate quests.  
  * QuestConfig will specify source ('Awakening' or 'Dungeon'), difficulty, focus (e.g., 'PULL\_VERTICAL'), dungeon\_level, daily modifiers, etc.  
  * This ensures all quest generation is consistent and reusable.

## **7\. API Specification (/v2/)**

The API will be RESTful and versioned. All endpoints will be organized into routers for clarity.

* **GET /v2/users/me/profile**: Returns the complete Profile Panel DTO.  
* **GET /v2/movements/library**: Returns the entire V2 skill tree library (from Redis cache).  
* **POST /v2/progression/unlock-skill**: Unlocks a skill node.  
* **POST /v2/awakening/generate**: Initiates the daily Awakening.  
* **POST /v2/dungeons/enter**: Enters a dungeon asynchronously.  
* **POST /v2/events/login**: Triggers the daily login reward logic.  
* **POST /v2/events/log-movement**: The re-implemented endpoint for logging reps.  
* **GET /health**: A simple health check endpoint to verify service status.

## **8\. Source Tree**

The project will follow a clean, modern Python application structure.

gategrind-api/  
├── app/                      \# Main application package  
│   ├── api/                  \# API layer: routers and controllers  
│   │   └── v2/  
│   ├── application/          \# Application layer: services & background tasks  
│   │   ├── services/  
│   │   └── tasks/  
│   ├── core/                 \# Core configuration and settings  
│   ├── domain/               \# Domain layer: models and schemas  
│   └── infrastructure/       \# Infrastructure layer: db, cache, etc.  
│       ├── db/  
│       └── repositories/  
├── tests/                    \# Test suite  
│   ├── integration/  
│   └── unit/  
├── .env.example              \# Environment variables template  
├── .github/workflows/ci.yaml \# CI pipeline  
├── main.py                   \# Application entry point  
└── pyproject.toml            \# Project dependencies and configuration

## **9\. Caching & Observability Strategy**

* **Caching (Redis)**: The primary use case for Redis will be to cache the entire **Movement & Skill Tree Library**. This data is read-heavy and changes rarely, making it a perfect candidate for caching to reduce database load and improve API response times.  
* **Observability (Sentry)**: Sentry will be integrated as a FastAPI middleware. It will automatically capture all unhandled exceptions from the application layer and above, providing real-time error alerts and detailed stack traces for rapid debugging.

## **10\. Next Steps**

This architecture document is the definitive technical blueprint. **Sarah, our Scrum Master**, will now take this document and the final PRD to begin the development process, starting with Epic 1\.