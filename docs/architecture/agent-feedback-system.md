# Agent Feedback Tracking System

## Purpose
Track agent interactions, decisions, and outcomes to improve performance over time.

## Feedback Categories

### 1. Story Review Feedback
Track the multi-agent story review process effectiveness.

### 2. Technical Decision Feedback
Document architectural and implementation decisions made by agents.

### 3. Quality Improvement Feedback
Capture what works well and what needs improvement.

## Feedback Entry Template

```markdown
## Feedback Entry - [Date] - [Agent] - [Category]

### Context
- **Story/Task**: [Story ID or task description]
- **Epic**: [Epic number and name]
- **Agents Involved**: [List of agents]

### What Happened
- **Initial Approach**: [What the agent(s) did]
- **Challenges Encountered**: [Problems or issues]
- **Resolution**: [How it was resolved]

### Outcome
- **Success Metrics**: [What went well]
- **Areas for Improvement**: [What could be better]
- **Time to Resolution**: [How long it took]

### Lessons Learned
- **For SM**: [Story drafting improvements]
- **For Dev**: [Technical review improvements]  
- **For QA**: [Testing review improvements]
- **For All**: [General process improvements]

### Action Items
- [ ] [Specific improvement to implement]
- [ ] [Process change needed]
- [ ] [Documentation update required]
```

## Feedback Collection Workflow

### After Each Story Review Cycle
1. **SM** logs feedback on story drafting effectiveness
2. **Dev** logs feedback on technical review process
3. **QA** logs feedback on testing review process
4. **All agents** note collaboration effectiveness

### Weekly Review Process
1. Review all feedback entries from the week
2. Identify patterns and recurring issues
3. Update agent contexts and processes
4. Implement improvements for next week

### Monthly Analysis
1. Analyze trends in agent performance
2. Update training materials and contexts
3. Refine collaboration workflows
4. Set improvement goals for next month

## Success Metrics to Track

### Story Quality Metrics
- Number of revision cycles needed
- Time from draft to "Ready for Development"
- Number of clarifying questions needed
- Post-development issues found

### Collaboration Metrics
- Agent response time in review cycles
- Quality of feedback provided
- Resolution rate of raised concerns
- Cross-agent communication effectiveness

### Process Efficiency Metrics
- Stories completed per sprint
- Rework rate after development starts
- Agent utilization and workload balance
- Overall project velocity

## Improvement Implementation

### Context Updates
When patterns emerge from feedback:
1. Update relevant agent context files
2. Add new guidelines or patterns
3. Refine collaboration workflows
4. Update quality checklists

### Process Refinements
Based on feedback analysis:
1. Adjust review cycle timing
2. Modify agent responsibilities
3. Improve handoff procedures
4. Enhance communication protocols

## Feedback Storage Structure

```
docs/agent-feedback/
├── 2024-01/
│   ├── story-reviews/
│   ├── technical-decisions/
│   └── process-improvements/
├── 2024-02/
│   ├── story-reviews/
│   ├── technical-decisions/
│   └── process-improvements/
└── analysis/
    ├── monthly-reports/
    └── improvement-tracking/
```

## Quick Feedback Commands

### For Agents to Use
- `*feedback-success` - Log a successful interaction
- `*feedback-issue` - Log a problem or challenge
- `*feedback-suggestion` - Suggest a process improvement
- `*feedback-review` - Review recent feedback trends

### For Users to Use
- `*feedback-summary` - Get summary of recent feedback
- `*feedback-trends` - See improvement trends
- `*feedback-actions` - View pending action items