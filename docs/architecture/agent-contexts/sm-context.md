# Story Manager (SM) Agent Context

## Role & Responsibilities
- Create draft stories from epic requirements
- Facilitate multi-agent story review workflow
- Ensure stories are development-ready before handoff
- Maintain story quality and consistency across epics

## Epic-Based Story Drafting Patterns

### Epic Structure Reference
Based on completed epics in this project:

#### Epic 1: Foundation
- **Pattern**: Infrastructure setup, database schema, service layer foundation
- **Story Types**: Database models, service architecture, API foundations
- **Key Dependencies**: Database setup → Service layer → API endpoints

#### Epic 2: Core Mechanics  
- **Pattern**: Re-implementing core features in V2 architecture
- **Story Types**: User registration, movement logging, XP calculation
- **Key Dependencies**: Foundation services → Feature implementation → Integration

#### Epic 3: Progression & Skill Tree
- **Pattern**: Game progression systems and user advancement
- **Story Types**: Skill trees, milestone progression, stat systems
- **Key Dependencies**: User system → XP engine → Progression mechanics

#### Epic 4: Aura Power Level System
- **Pattern**: Calculated metrics and real-time updates
- **Story Types**: Calculation engines, real-time updates, API integration
- **Key Dependencies**: User stats → Calculation logic → Real-time updates

#### Epic 5: Awakening & Dungeon Systems
- **Pattern**: Daily systems and endgame content
- **Story Types**: Daily challenges, quest generation, reward systems
- **Key Dependencies**: User progression → Quest system → Reward mechanics

## Story Drafting Guidelines

### Story Structure Template
```markdown
# Story X.Y: [Title]

**Epic:** [Epic Name]
**Priority:** [High/Medium/Low]
**Points:** [1-8]
**Status:** Draft

## Story Statement
As a [user type], I want [functionality], so that [business value].

## Acceptance Criteria
1. [Specific, testable criteria]
2. [Technical requirements]
3. [Integration requirements]

## Dev Notes
### Technical Implementation
- [Architecture decisions from codebase-context.md]
- [V2 patterns to follow]
- [Database schema requirements]
- [Service layer integration]

### Dependencies
- [Previous stories required]
- [External systems]
- [Database migrations]

### Testing Requirements
- [Unit test coverage]
- [Integration test scenarios]
- [API endpoint testing]
```

### V2 Implementation Patterns (Reference codebase-context.md)
- **Models**: Use `/app/infrastructure/database/models/v2/`
- **Services**: Use `/app/application/services/`
- **Schemas**: Use `/app/api/v2/schemas/`
- **Endpoints**: Use `/app/api/v2/endpoints/`
- **Testing**: Follow 93% coverage standard with Pytest + FastAPI TestClient

## Multi-Agent Collaboration Workflow

### Phase 1: SM Draft Creation
**SM Responsibilities:**
1. Create initial story draft from epic requirements
2. Include technical context from codebase-context.md
3. Define clear acceptance criteria
4. Set initial story points estimate
5. Mark status as "Draft - Ready for Review"

### Phase 2: Dev Review
**Dev Agent Responsibilities:**
1. Review technical feasibility
2. Validate V2 architecture alignment
3. Check dependency accuracy
4. Ask clarifying questions about:
   - Database schema requirements
   - Service integration points
   - API endpoint specifications
   - Testing approach
5. Provide feedback on story points estimate

**Dev Review Format:**
```markdown
## Dev Review - [Date]
### Technical Feasibility: ✅/❌
### Architecture Alignment: ✅/❌
### Dependencies Validated: ✅/❌

### Questions/Concerns:
1. [Specific technical question]
2. [Implementation concern]

### Recommendations:
- [Technical suggestions]
- [Architecture improvements]

### Story Points Assessment: [Agree/Suggest X points]
```

### Phase 3: QA Review
**QA Agent Responsibilities:**
1. Review testability of acceptance criteria
2. Identify edge cases and error scenarios
3. Validate testing requirements
4. Suggest additional test coverage
5. Review integration testing needs

**QA Review Format:**
```markdown
## QA Review - [Date]
### Testability: ✅/❌
### Acceptance Criteria Clarity: ✅/❌
### Edge Cases Identified: ✅/❌

### Testing Recommendations:
- [Unit test scenarios]
- [Integration test cases]
- [Edge cases to cover]

### Additional Acceptance Criteria Needed:
1. [Missing criteria]
2. [Error handling requirements]
```

### Phase 4: SM Revision
**SM Responsibilities:**
1. Address Dev and QA feedback
2. Update story with clarifications
3. Revise acceptance criteria
4. Adjust story points if needed
5. Mark as "Draft - Revised"

### Phase 5: Final Approval
**Approval Criteria:**
- ✅ Dev approves technical approach
- ✅ QA approves testing strategy
- ✅ All questions resolved
- ✅ Dependencies validated
- ✅ Story points agreed upon

**Final Status:** "Ready for Development"

## Common Story Patterns by Epic Type

### Foundation Stories
- Database schema creation
- Service layer setup
- API endpoint foundations
- Migration scripts
- Seeding data

### Feature Implementation Stories
- User-facing functionality
- Business logic implementation
- API endpoint creation
- Frontend integration
- Real-time updates

### System Integration Stories
- Cross-service communication
- External API integration
- Event handling
- Caching implementation
- Performance optimization

## Quality Checklist for Story Drafts

### Technical Completeness
- [ ] References correct V2 architecture patterns
- [ ] Includes database schema requirements
- [ ] Specifies service layer integration
- [ ] Defines API endpoint structure
- [ ] Includes migration requirements

### Clarity & Testability
- [ ] Acceptance criteria are specific and measurable
- [ ] Edge cases are considered
- [ ] Error handling is specified
- [ ] Testing approach is defined
- [ ] Dependencies are clearly stated

### Development Readiness
- [ ] No ambiguous requirements
- [ ] Technical approach is validated
- [ ] Story points are realistic
- [ ] All questions are resolved
- [ ] Ready for immediate development

## Reference Files
- `docs/architecture/codebase-context.md` - V2 implementation patterns
- `docs/stories/` - Completed story examples
- `docs/prd/` - Epic requirements and context