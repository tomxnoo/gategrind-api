# GateGrind V2 Backend Architecture Overview

## Introduction

The **GateGrind V2 Backend** is a "Brownfield x Greenfield" project that combines the re-implementation of existing V1 features with the development of entirely new game systems. This architecture document serves as the definitive technical blueprint for the V2 backend implementation.

## Project Philosophy

This project embodies a **"Brownfield x Greenfield"** approach:
- **Brownfield**: Re-implementing existing V1 features (Movement Logging, XP Engine, Incursions) with improved architecture
- **Greenfield**: Building entirely new game systems (Awakening, Dungeons, Aura, Skill Tree) from scratch

## High-Level System Architecture

The GateGrind V2 backend follows a **Hexagonal Architecture** (Ports and Adapters) pattern, ensuring clean separation of concerns and testability.

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Discord Bot   │    │   Web Client    │    │  External APIs  │
│    (Client)     │    │    (Client)     │    │    (Client)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     FastAPI Application   │
                    │   (Hexagonal Architecture)│
                    └─────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    ┌─────┴─────┐         ┌──────┴──────┐        ┌─────┴─────┐
    │  NeonDB   │         │    Redis    │        │  Sentry   │
    │(Database) │         │  (Cache)    │        │(Monitoring)│
    └───────────┘         └─────────────┘        └───────────┘
```

### Core Architectural Principles

1. **API-First Design**: All functionality exposed through well-defined REST endpoints
2. **Hexagonal Architecture**: Clean separation between business logic and external concerns
3. **Domain-Driven Design**: Business logic encapsulated in domain entities and services
4. **Dependency Inversion**: High-level modules don't depend on low-level modules
5. **Single Responsibility**: Each component has a clear, focused purpose

## Key Features

### V2 Greenfield Features
- **Awakening System**: Daily ritual and quest generation
- **Dungeon System**: Shadow Key-based dungeon exploration
- **Aura System**: Power level calculation and real-time updates
- **Skill Tree**: Progressive movement unlocking system

### V1 Brownfield Re-implementation
- **Movement Logging**: Enhanced rep tracking system
- **XP Engine**: Improved experience and progression mechanics
- **Incursions**: Redesigned group challenge system

## Architecture Benefits

1. **Maintainability**: Clear separation of concerns makes code easier to understand and modify
2. **Testability**: Hexagonal architecture enables comprehensive unit and integration testing
3. **Scalability**: Modular design supports horizontal scaling and feature expansion
4. **Performance**: Redis caching and optimized database queries ensure fast response times
5. **Observability**: Integrated Sentry monitoring provides real-time error tracking

## Development Approach

The V2 backend will be developed through **six sequential epics**, each building upon the previous foundation:

1. **Foundation**: Database schema and core service layer
2. **Core Mechanics**: V1 feature re-implementation
3. **Progression**: Skill tree and user advancement
4. **Aura System**: Power level calculation
5. **Awakening & Dungeons**: New gameplay systems
6. **Integration**: Discord bot connectivity

## Next Steps

This overview provides the foundation for understanding the GateGrind V2 architecture. For detailed implementation guidance, refer to the specific architecture documents in this directory.

---
*This architecture supports the GateGrind ecosystem's vision of creating an engaging, scalable fitness gaming platform.*