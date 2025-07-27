# Agent Workflow Enforcement System

## Purpose
Enforce strict adherence to agent workflow rules, particularly for the dev agent's sub-task completion requirements. Prevent agents from skipping steps, completing full tasks without individual sub-task validation, and ensure quality gates are met at each step.

## Critical Dev Agent Workflow Rules

### Sub-Task Completion Protocol
```yaml
dev_workflow_enforcement:
  sub_task_sequence:
    rule: "MUST complete each sub-task individually before proceeding"
    validation: "Each sub-task must be marked [x] with validation proof"
    testing: "Each sub-task must include test execution and results"
    blocking: "Cannot proceed to next sub-task until current is validated"
  
  task_completion_order:
    rule: "MUST complete all sub-tasks before marking main task complete"
    validation: "All sub-tasks [x] checked with evidence"
    testing: "Integration tests pass for completed sub-tasks"
    blocking: "Cannot mark task complete until all sub-tasks validated"
  
  quality_gates:
    rule: "MUST pass quality gates at each sub-task"
    validation: "Code quality, tests, documentation complete"
    testing: "Unit tests, integration tests, performance checks"
    blocking: "Cannot proceed without passing all quality gates"
```

### Enforcement Mechanisms

#### 1. Pre-Execution Validation
```yaml
pre_execution_checks:
  story_analysis:
    - Parse story file for tasks and sub-tasks
    - Identify current position in workflow
    - Validate prerequisites are met
    - Check for blocking dependencies
  
  workflow_state:
    - Verify previous sub-task completion
    - Check test execution status
    - Validate quality gate passage
    - Confirm documentation updates
  
  agent_compliance:
    - Review agent's stated plan
    - Validate plan follows sub-task sequence
    - Check for workflow shortcuts
    - Ensure testing is included
```

#### 2. Real-Time Monitoring
```yaml
execution_monitoring:
  sub_task_tracking:
    - Monitor checkbox state changes
    - Validate completion evidence
    - Track test execution
    - Monitor code changes
  
  workflow_violations:
    - Detect skipped sub-tasks
    - Identify missing tests
    - Flag incomplete validations
    - Alert on quality gate failures
  
  intervention_triggers:
    - Agent attempts to skip sub-task
    - No test execution for completed sub-task
    - Quality gates not met
    - Documentation not updated
```

#### 3. Post-Completion Validation
```yaml
completion_validation:
  sub_task_verification:
    - Verify checkbox marked [x]
    - Validate completion evidence exists
    - Check test results are documented
    - Confirm code changes are appropriate
  
  quality_assurance:
    - Run automated quality checks
    - Verify test coverage requirements
    - Check code quality metrics
    - Validate documentation updates
  
  progression_approval:
    - All validations pass
    - Quality gates met
    - Evidence documented
    - Ready for next sub-task
```

## Workflow Enforcement Rules

### Dev Agent Specific Rules
```yaml
dev_agent_rules:
  sub_task_completion:
    mandatory_steps:
      1. "Read and understand sub-task requirements"
      2. "Plan implementation approach"
      3. "Implement code changes"
      4. "Write/update unit tests"
      5. "Execute tests and verify results"
      6. "Update documentation if needed"
      7. "Mark sub-task [x] with evidence"
      8. "HALT and await validation before next sub-task"
    
    blocking_conditions:
      - "Cannot proceed without completing all 8 steps"
      - "Cannot mark [x] without test execution proof"
      - "Cannot start next sub-task without validation"
      - "Cannot complete task without all sub-tasks [x]"
  
  testing_requirements:
    unit_tests:
      - "Every code change must have unit tests"
      - "Tests must pass before marking sub-task complete"
      - "Test coverage must meet minimum threshold"
    
    integration_tests:
      - "Sub-tasks affecting APIs must include integration tests"
      - "Database changes must include migration tests"
      - "Service layer changes must include service tests"
    
    validation_evidence:
      - "Test execution output must be documented"
      - "Code quality metrics must be recorded"
      - "Performance impact must be assessed"
```

### Quality Gate Enforcement
```yaml
quality_gates:
  code_quality:
    linting: "Zero linting errors allowed"
    type_checking: "Zero type checking errors allowed"
    complexity: "Cyclomatic complexity ≤ 10"
    coverage: "Test coverage ≥ 80%"
  
  testing:
    unit_tests: "All unit tests must pass"
    integration_tests: "All integration tests must pass"
    performance_tests: "No performance regressions"
    security_tests: "No security vulnerabilities"
  
  documentation:
    code_comments: "Complex logic must be commented"
    api_docs: "API changes must update documentation"
    readme_updates: "Breaking changes must update README"
    changelog: "Changes must be logged"
```

## Enforcement Implementation

### 1. Story Parser and Validator
```python
class StoryWorkflowEnforcer:
    def __init__(self, story_path: str):
        self.story_path = story_path
        self.story_content = self.load_story()
        self.tasks = self.parse_tasks()
        self.sub_tasks = self.parse_sub_tasks()
    
    def validate_current_position(self) -> Dict[str, Any]:
        """Validate current position in workflow"""
        return {
            "current_task": self.get_current_task(),
            "current_sub_task": self.get_current_sub_task(),
            "completed_sub_tasks": self.get_completed_sub_tasks(),
            "next_required_action": self.get_next_action(),
            "blocking_issues": self.get_blocking_issues()
        }
    
    def can_proceed_to_next_sub_task(self) -> bool:
        """Check if agent can proceed to next sub-task"""
        current_sub_task = self.get_current_sub_task()
        return (
            current_sub_task.is_complete() and
            current_sub_task.has_test_evidence() and
            current_sub_task.passes_quality_gates() and
            current_sub_task.has_documentation()
        )
```

### 2. Real-Time Workflow Monitor
```python
class WorkflowMonitor:
    def __init__(self, agent_id: str, story_path: str):
        self.agent_id = agent_id
        self.enforcer = StoryWorkflowEnforcer(story_path)
        self.violations = []
    
    def monitor_agent_actions(self, action: str, context: Dict[str, Any]):
        """Monitor agent actions for workflow violations"""
        if action == "mark_sub_task_complete":
            self.validate_sub_task_completion(context)
        elif action == "start_next_sub_task":
            self.validate_progression_allowed(context)
        elif action == "mark_task_complete":
            self.validate_task_completion(context)
    
    def validate_sub_task_completion(self, context: Dict[str, Any]):
        """Validate sub-task completion requirements"""
        violations = []
        
        if not context.get("tests_executed"):
            violations.append("Sub-task marked complete without test execution")
        
        if not context.get("quality_gates_passed"):
            violations.append("Sub-task marked complete without passing quality gates")
        
        if not context.get("evidence_documented"):
            violations.append("Sub-task marked complete without evidence documentation")
        
        if violations:
            self.block_action("sub_task_completion", violations)
```

### 3. Agent Intervention System
```python
class AgentInterventionSystem:
    def __init__(self):
        self.intervention_rules = self.load_intervention_rules()
        self.escalation_levels = ["warning", "blocking", "escalation"]
    
    def intervene(self, violation_type: str, details: Dict[str, Any]):
        """Intervene when workflow violations detected"""
        intervention_level = self.determine_intervention_level(violation_type)
        
        if intervention_level == "warning":
            self.send_warning(details)
        elif intervention_level == "blocking":
            self.block_action(details)
        elif intervention_level == "escalation":
            self.escalate_to_user(details)
    
    def block_action(self, details: Dict[str, Any]):
        """Block agent action and require compliance"""
        return {
            "action": "BLOCKED",
            "reason": details["violation"],
            "required_actions": details["required_compliance"],
            "cannot_proceed_until": details["compliance_requirements"]
        }
```

## Compliance Validation Checkpoints

### Sub-Task Level Checkpoints
```yaml
sub_task_checkpoints:
  start_validation:
    - Previous sub-task completed and validated
    - Prerequisites met
    - Dependencies resolved
    - Clear understanding of requirements
  
  implementation_validation:
    - Code changes align with sub-task requirements
    - Implementation follows coding standards
    - No breaking changes introduced
    - Performance impact assessed
  
  testing_validation:
    - Unit tests written and passing
    - Integration tests updated if needed
    - Test coverage meets requirements
    - No test regressions introduced
  
  completion_validation:
    - All requirements met
    - Tests passing
    - Documentation updated
    - Quality gates passed
    - Evidence documented
```

### Task Level Checkpoints
```yaml
task_checkpoints:
  all_sub_tasks_complete:
    - Every sub-task marked [x]
    - All sub-task evidence documented
    - All tests passing
    - No quality gate failures
  
  integration_validation:
    - All sub-tasks work together
    - Integration tests passing
    - No system regressions
    - Performance benchmarks met
  
  acceptance_criteria_met:
    - All acceptance criteria validated
    - User stories satisfied
    - Edge cases handled
    - Error scenarios tested
```

## Enforcement Configuration

### Agent-Specific Rules
```yaml
agent_enforcement_config:
  dev_agent:
    strict_mode: true
    sub_task_enforcement: mandatory
    testing_requirements: strict
    quality_gates: enforced
    documentation: required
    
    blocking_violations:
      - skip_sub_task
      - no_test_execution
      - quality_gate_failure
      - missing_documentation
    
    warning_violations:
      - incomplete_evidence
      - minor_quality_issues
      - documentation_gaps
  
  sm_agent:
    workflow_monitoring: enabled
    progress_validation: strict
    quality_oversight: enforced
    escalation_authority: true
```

### Escalation Procedures
```yaml
escalation_procedures:
  level_1_warning:
    trigger: "Minor workflow deviation"
    action: "Send warning message to agent"
    retry_allowed: true
    
  level_2_blocking:
    trigger: "Major workflow violation"
    action: "Block agent action, require compliance"
    retry_allowed: true
    escalation_timeout: 30_minutes
    
  level_3_escalation:
    trigger: "Repeated violations or critical failure"
    action: "Escalate to user, suspend agent"
    manual_intervention: required
    incident_logging: mandatory
```

## Success Metrics

### Workflow Compliance
- Sub-task sequence adherence: > 98%
- Testing requirement compliance: > 95%
- Quality gate passage rate: > 95%
- Documentation completion rate: > 90%

### Agent Effectiveness
- Workflow violation reduction: > 80%
- Time to compliance: < 5 minutes
- Escalation rate: < 2%
- User intervention required: < 1%

### System Reliability
- Enforcement system uptime: > 99.9%
- False positive rate: < 1%
- Response time: < 2 seconds
- Audit trail completeness: 100%