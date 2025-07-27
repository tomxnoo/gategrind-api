# Auto-Context Loader System

## Purpose
Automatically loads comprehensive workspace context when agents activate, ensuring they have complete awareness of:
- Current project state and active stories
- Recent handoffs and decisions
- Workspace progress and quality metrics
- Architecture and technical context
- Agent workflow compliance requirements

## Auto-Loading Triggers

### Agent Activation Context
When any agent activates, automatically load:

1. **Core Configuration Context**
   - Load all files from `devLoadAlwaysFiles` and `smLoadAlwaysFiles` in core-config.yaml
   - Current workspace status from WORKSPACE_STATUS.md
   - Active session information from .workspace/sessions/

2. **Story and Progress Context**
   - Current active stories from docs/stories/
   - Recent handoffs from .workspace/handoffs/
   - Progress tracking from .workspace/progress/
   - Quality metrics from .workspace/quality/

3. **Architecture Context**
   - Codebase context and technical stack
   - Project structure and coding standards
   - API specifications and design patterns

4. **Workflow Compliance Context**
   - Agent-specific workflow rules
   - Task validation requirements
   - Quality gates and checkpoints

## Implementation Strategy

### 1. Context Detection Engine
```yaml
context_detection:
  workspace_status:
    - Check WORKSPACE_STATUS.md for current phase
    - Identify active stories and completion status
    - Load recent handoff packages
  
  agent_specific:
    - Load agent-specific context files
    - Apply role-based context filtering
    - Include relevant workflow rules
  
  project_state:
    - Detect current development phase
    - Load relevant architecture docs
    - Include active technical decisions
```

### 2. Smart Context Prioritization
```yaml
priority_loading:
  critical_always:
    - Current story being worked on
    - Recent handoffs (last 3)
    - Active quality issues
    - Blocking dependencies
  
  role_specific:
    dev_agent:
      - Technical architecture docs
      - Coding standards and patterns
      - Test requirements and coverage
      - Performance benchmarks
    
    sm_agent:
      - Project progress and metrics
      - Story prioritization
      - Team coordination context
      - Quality validation results
```

### 3. Context Freshness Validation
```yaml
freshness_checks:
  workspace_status:
    max_age: 24_hours
    auto_refresh: true
    stale_warning: true
  
  handoffs:
    max_age: 7_days
    include_recent: 5
    archive_old: true
  
  architecture_docs:
    max_age: 30_days
    version_check: true
    update_notification: true
```

## Auto-Context Loading Protocol

### Phase 1: Immediate Context (< 2 seconds)
1. Load workspace status and current focus
2. Identify active story and current task
3. Load recent handoff (if any)
4. Apply agent-specific context filter

### Phase 2: Comprehensive Context (< 5 seconds)
1. Load all devLoadAlwaysFiles/smLoadAlwaysFiles
2. Load relevant architecture documentation
3. Load progress and quality metrics
4. Load workflow compliance rules

### Phase 3: Contextual Awareness (< 10 seconds)
1. Analyze loaded context for relevance
2. Identify potential blockers or dependencies
3. Prepare agent-specific recommendations
4. Validate context completeness

## Context Loading Rules

### For Dev Agent
```yaml
dev_context_loading:
  mandatory:
    - Current story with all sub-tasks
    - Technical architecture docs
    - Coding standards and patterns
    - Test requirements and coverage
    - Recent handoff context
  
  conditional:
    - Related stories (if dependencies exist)
    - Performance benchmarks (if performance story)
    - Security requirements (if security-related)
    - Database schema (if data changes)
  
  workflow_enforcement:
    - Sub-task validation rules
    - Testing requirements per sub-task
    - Quality gate checkpoints
    - Completion validation criteria
```

### For SM Agent
```yaml
sm_context_loading:
  mandatory:
    - All active stories and progress
    - Team coordination context
    - Quality metrics and issues
    - Project timeline and milestones
  
  conditional:
    - Stakeholder communication (if external dependencies)
    - Risk assessment (if blockers exist)
    - Resource allocation (if capacity issues)
    - Technical debt tracking (if quality concerns)
```

## Context Validation and Monitoring

### Context Completeness Check
```yaml
validation_rules:
  required_context:
    - workspace_status: present
    - current_story: identified
    - agent_workflow: loaded
    - architecture_docs: current_version
  
  quality_gates:
    - context_age: < 24_hours
    - completeness: > 90%
    - relevance_score: > 0.8
    - workflow_rules: enforced
```

### Context Loading Metrics
```yaml
monitoring:
  loading_time:
    target: < 10_seconds
    warning: > 15_seconds
    error: > 30_seconds
  
  context_quality:
    completeness: track_percentage
    relevance: track_score
    freshness: track_age
  
  agent_compliance:
    workflow_adherence: track_percentage
    sub_task_completion: track_sequence
    quality_gate_passage: track_success_rate
```

## Integration Points

### Claude Code Integration
```yaml
claude_code_hooks:
  agent_activation:
    - Trigger auto-context loading
    - Display context loading progress
    - Show context summary
    - Validate context completeness
  
  session_continuity:
    - Preserve loaded context
    - Update context on changes
    - Sync context across sessions
    - Handle context conflicts
```

### Workspace Integration
```yaml
workspace_hooks:
  story_changes:
    - Reload story context
    - Update progress tracking
    - Refresh quality metrics
    - Notify active agents
  
  handoff_creation:
    - Update context for target agent
    - Preserve handoff context
    - Validate handoff completeness
    - Archive previous context
```

## Error Handling and Fallbacks

### Context Loading Failures
```yaml
error_handling:
  partial_loading:
    - Continue with available context
    - Log missing context items
    - Provide fallback context
    - Request manual context loading
  
  complete_failure:
    - Use cached context (if available)
    - Provide minimal context
    - Request user intervention
    - Log error for investigation
```

### Context Conflicts
```yaml
conflict_resolution:
  version_conflicts:
    - Use most recent version
    - Log conflict details
    - Request user resolution
    - Provide conflict summary
  
  agent_conflicts:
    - Apply agent-specific priority
    - Merge compatible contexts
    - Escalate unresolvable conflicts
    - Maintain audit trail
```

## Success Metrics

### Context Loading Success
- Loading time < 10 seconds (95th percentile)
- Context completeness > 95%
- Context relevance score > 0.9
- Zero critical context failures

### Agent Effectiveness
- Workflow compliance > 95%
- Sub-task completion sequence adherence > 98%
- Quality gate passage rate > 95%
- Context-driven decision accuracy > 90%

### System Reliability
- Context loading availability > 99.9%
- Context freshness < 1 hour average age
- Error recovery success rate > 95%
- Context conflict resolution < 5 minutes