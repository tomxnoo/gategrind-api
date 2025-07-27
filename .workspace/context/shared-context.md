# Shared Workspace Context

## Project Overview
**Project:** RoS-TRAE (Realm of Shadows - TRAE)  
**Type:** Brownfield x Greenfield Game Development Platform  
**Architecture:** V1/V2 Mixed Architecture with V2 Migration Focus  

## Current Development Context

### Active Development Focus
- **Primary Goal:** V2 API Development and V1 Legacy Integration
- **Architecture:** Hexagonal Architecture with Clean Code Principles
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Framework:** FastAPI for V2 API, Discord.py for V1 Bot

### Key Directories
```
├── app/                    # V2 FastAPI Application
├── api/                    # V2 API Routes and Models
├── core/                   # Shared Core Components
├── features/               # V1 Discord Bot Features
├── docs/                   # Documentation
│   ├── ai/                 # AI Agent Documentation
│   ├── architecture/       # Architecture Documentation
│   └── prd/               # Product Requirements
├── bmad-core/             # Agent Configuration and Workflows
└── .workspace/            # Workspace Management
```

### Development Standards
- **Code Quality:** Zero-defect implementation standards
- **Testing:** Comprehensive unit, integration, and performance testing
- **Architecture:** V2 components preferred, V1 legacy maintenance only
- **Database:** ACID compliance, performance optimization
- **Security:** Input validation, authentication, authorization

### Current Sprint Context
- **Focus:** Core V2 API stabilization
- **Priority:** Database optimization and performance
- **Testing:** Comprehensive test coverage for new features
- **Documentation:** Architecture and API documentation updates

### Workflow Enforcement
- **Sub-task Protocol:** Individual sub-task completion with validation
- **Quality Gates:** All tests must pass before progression
- **Evidence Required:** Test execution proof for each implementation
- **Halt Points:** Validation required between sub-tasks

## Agent Context
- **Primary Agent:** Enhanced Dev Agent (James)
- **Workflow:** Strict sub-task validation protocol
- **Standards:** Zero-defect implementation with mathematical precision
- **Focus:** Complex story execution with systematic validation

## Recent Changes
- Core configuration cleanup and validation
- Workspace file structure standardization
- Agent workflow enforcement implementation
- V2 architecture documentation updates

---
*Last Updated: 2025-01-27*  
*Context Version: 1.0*