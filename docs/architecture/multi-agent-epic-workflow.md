# Multi-Agent Epic Drafting Workflow

## Overview
Collaborative process for creating high-quality epic drafts using specialized agent expertise.

## Agent Roles in Epic Drafting

### Story Manager (SM) - Lead
- **Primary Responsibility**: Create initial epic draft
- **Expertise**: Epic structure, story sequencing, business value
- **Focus**: User stories, acceptance criteria, epic coherence

### Developer (Dev) - Technical Reviewer  
- **Primary Responsibility**: Technical feasibility and architecture review
- **Expertise**: Implementation complexity, technical dependencies, V2 patterns
- **Focus**: Technical approach, effort estimation, architectural alignment

### QA - Quality & Risk Reviewer
- **Primary Responsibility**: Quality assurance and risk assessment
- **Expertise**: Testing strategy, edge cases, integration risks
- **Focus**: Testability, quality gates, risk mitigation

## Epic Drafting Workflow

### Phase 1: SM Epic Draft Creation
**Duration**: 1-2 hours
**SM Responsibilities**:
1. Analyze epic requirements from PRD
2. Create epic structure with story breakdown
3. Define story sequence and dependencies
4. Write initial user stories with acceptance criteria
5. Estimate epic scope and timeline
6. Mark as "Draft - Ready for Review"

**Epic Draft Template**:
```markdown
# Epic X: [Epic Name]

## Epic Goal
[2-3 sentences describing objective and business value]

## Epic Scope
- **Duration**: [Estimated weeks]
- **Story Count**: [Number of stories]
- **Complexity**: [High/Medium/Low]

## Story Breakdown
### Story X.1: [Foundation Story]
- **Type**: Foundation/Setup
- **Dependencies**: [Previous epic completion]
- **Acceptance Criteria**: [Key criteria]

### Story X.2: [Core Feature Story]
- **Type**: Feature Implementation
- **Dependencies**: [Story X.1]
- **Acceptance Criteria**: [Key criteria]

[Continue for all stories...]

## Epic Dependencies
- **Previous Epics**: [Required completions]
- **External Systems**: [Third-party dependencies]
- **Infrastructure**: [Required setup]

## Success Criteria
1. [Measurable epic outcome]
2. [Business value delivered]
3. [Technical milestone achieved]

## Risks & Mitigation
- **Risk**: [Potential issue]
  - **Mitigation**: [How to address]
```

### Phase 2: Dev Technical Review
**Duration**: 30-60 minutes
**Dev Responsibilities**:
1. Review technical feasibility of each story
2. Validate V2 architecture alignment
3. Assess implementation complexity
4. Identify technical dependencies and risks
5. Provide effort estimation feedback
6. Ask clarifying questions

**Dev Review Template**:
```markdown
## Dev Technical Review - [Date]

### Epic Feasibility Assessment
- **Overall Complexity**: [High/Medium/Low]
- **Architecture Alignment**: ✅/❌
- **V2 Pattern Compliance**: ✅/❌
- **Estimated Epic Duration**: [X weeks]

### Story-by-Story Analysis
#### Story X.1: [Story Name]
- **Complexity**: [1-8 points]
- **Technical Concerns**: [Issues or questions]
- **Dependencies**: [Technical prerequisites]
- **Recommendations**: [Suggestions]

[Repeat for each story...]

### Technical Questions for SM
1. [Specific implementation question]
2. [Architecture clarification needed]
3. [Dependency clarification]

### Technical Recommendations
- [Architecture suggestions]
- [Implementation approach]
- [Risk mitigation strategies]

### Approval Status
- [ ] Ready for QA Review
- [ ] Needs SM Clarification (see questions above)
```

### Phase 3: QA Quality & Risk Review
**Duration**: 30-45 minutes
**QA Responsibilities**:
1. Review testability of epic and stories
2. Identify quality risks and edge cases
3. Assess integration testing complexity
4. Validate acceptance criteria completeness
5. Suggest quality gates and checkpoints

**QA Review Template**:
```markdown
## QA Quality & Risk Review - [Date]

### Epic Quality Assessment
- **Testability**: ✅/❌
- **Acceptance Criteria Quality**: ✅/❌
- **Integration Risk**: [High/Medium/Low]
- **Quality Gate Complexity**: [High/Medium/Low]

### Story Quality Analysis
#### Story X.1: [Story Name]
- **Testability Score**: [1-5]
- **Edge Cases Identified**: [List]
- **Testing Complexity**: [High/Medium/Low]
- **Quality Concerns**: [Issues]

[Repeat for each story...]

### Quality Questions for SM
1. [Acceptance criteria clarification]
2. [Edge case handling question]
3. [Integration testing approach]

### Quality Recommendations
- **Testing Strategy**: [Approach suggestions]
- **Quality Gates**: [Checkpoints to add]
- **Risk Mitigation**: [Quality risk solutions]
- **Additional Acceptance Criteria**: [Missing criteria]

### Approval Status
- [ ] Ready for SM Revision
- [ ] Needs SM Clarification (see questions above)
```

### Phase 4: SM Epic Revision
**Duration**: 30-60 minutes
**SM Responsibilities**:
1. Address all Dev and QA feedback
2. Clarify questions and concerns
3. Update story acceptance criteria
4. Revise epic structure if needed
5. Adjust timeline and scope estimates
6. Mark as "Draft - Revised"

### Phase 5: Final Review Cycle
**Duration**: 15-30 minutes each
**Process**:
1. **Dev Final Review**: Validate technical concerns addressed
2. **QA Final Review**: Confirm quality issues resolved
3. **SM Final Polish**: Make final adjustments

### Phase 6: Epic Approval
**Approval Criteria**:
- ✅ Dev approves technical approach and feasibility
- ✅ QA approves quality strategy and testability
- ✅ All questions and concerns resolved
- ✅ Epic structure and story sequence validated
- ✅ Timeline and scope estimates agreed upon

**Final Status**: "Ready for Story Development"

## Epic Quality Gates

### Technical Quality Gates (Dev)
- [ ] All stories follow V2 architecture patterns
- [ ] Technical dependencies clearly identified
- [ ] Implementation approach is feasible
- [ ] Effort estimates are realistic
- [ ] No architectural conflicts

### Quality Assurance Gates (QA)
- [ ] All stories have testable acceptance criteria
- [ ] Edge cases and error scenarios considered
- [ ] Integration testing approach defined
- [ ] Quality risks identified and mitigated
- [ ] Testing complexity is manageable

### Epic Structure Gates (SM)
- [ ] Stories are logically sequenced
- [ ] Dependencies are properly mapped
- [ ] Business value is clearly articulated
- [ ] Epic scope is appropriate
- [ ] Timeline is realistic

## Collaboration Best Practices

### Communication Guidelines
- **Be Specific**: Ask precise questions, provide detailed feedback
- **Be Constructive**: Focus on improvement, not criticism
- **Be Timely**: Complete reviews within agreed timeframes
- **Be Collaborative**: Work together toward the best solution

### Feedback Quality Standards
- **Technical Feedback**: Include specific implementation concerns
- **Quality Feedback**: Provide actionable testing recommendations
- **Process Feedback**: Suggest concrete workflow improvements

### Escalation Process
If consensus cannot be reached:
1. **Technical Disputes**: Architect agent consultation
2. **Quality Disputes**: Senior QA review
3. **Scope Disputes**: Product Owner consultation
4. **Timeline Disputes**: Project Manager consultation

## Success Metrics

### Epic Quality Metrics
- Time from draft to approval
- Number of revision cycles needed
- Post-development issues discovered
- Epic completion rate vs. estimates

### Collaboration Metrics
- Agent response time in reviews
- Quality of feedback provided
- Resolution rate of concerns raised
- Cross-agent communication effectiveness

## Continuous Improvement

### Weekly Retrospectives
- Review epic drafting effectiveness
- Identify process bottlenecks
- Celebrate successful collaborations
- Plan process improvements

### Monthly Process Updates
- Update workflow based on lessons learned
- Refine agent responsibilities
- Improve collaboration templates
- Enhance quality gates