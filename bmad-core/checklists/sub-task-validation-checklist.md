# Sub-Task Validation Checklist

## Purpose
Enforce strict sub-task completion protocol for dev agents to prevent bulk task completion and ensure proper testing at each step.

## CRITICAL SUB-TASK RULES

### ✅ Pre-Sub-Task Validation
```yaml
BEFORE_STARTING_SUB_TASK:
  □ Previous sub-task is marked [x] and validated
  □ Current sub-task requirements clearly understood
  □ Implementation approach planned and documented
  □ Testing strategy defined for this sub-task
  □ Dependencies identified and resolved
  □ Scope limited to ONLY current sub-task
```

### ✅ During Sub-Task Implementation
```yaml
DURING_IMPLEMENTATION:
  □ Code changes align ONLY with current sub-task
  □ No scope creep beyond current sub-task boundaries
  □ Coding standards and conventions followed
  □ Error handling implemented appropriately
  □ Comments and documentation added for clarity
  □ No changes made to other sub-tasks
```

### ✅ Sub-Task Testing Requirements
```yaml
TESTING_VALIDATION:
  □ Unit tests written for sub-task changes
  □ Unit tests executed and passing
  □ Integration tests updated if needed
  □ Integration tests executed and passing
  □ Manual testing performed if applicable
  □ Test coverage meets minimum requirements (≥80%)
  □ No regressions introduced
  □ Performance impact assessed
```

### ✅ Sub-Task Completion Validation
```yaml
COMPLETION_VALIDATION:
  □ All sub-task requirements implemented
  □ All tests passing with evidence
  □ Code quality checks passed
  □ Documentation updated appropriately
  □ Debug Log updated with implementation details
  □ Evidence of testing documented
  □ Sub-task marked [x] in story file
  □ HALT executed - waiting for validation
```

### ✅ Evidence Documentation Requirements
```yaml
EVIDENCE_DOCUMENTATION:
  □ Implementation approach documented
  □ Code changes summarized
  □ Test execution results provided
  □ Performance impact noted
  □ Any issues encountered and resolved
  □ Time spent on sub-task recorded
  □ Next sub-task dependencies identified
```

## BLOCKING CONDITIONS

### 🚫 NEVER ALLOWED
```yaml
FORBIDDEN_ACTIONS:
  □ Completing multiple sub-tasks in one session
  □ Marking sub-tasks [x] without testing
  □ Proceeding to next sub-task without validation
  □ Bulk completion of task without sub-task breakdown
  □ Skipping test execution for any sub-task
  □ Implementing beyond current sub-task scope
  □ Modifying other tasks while working on current sub-task
```

### 🛑 MANDATORY HALTS
```yaml
MUST_HALT_FOR:
  □ Sub-task completion without testing evidence
  □ Test failures that cannot be immediately resolved
  □ Scope creep beyond current sub-task
  □ Missing dependencies that block progress
  □ Quality gates not met
  □ Unclear requirements that need clarification
  □ Any attempt to skip validation steps
```

## VALIDATION CHECKPOINTS

### Checkpoint 1: Sub-Task Understanding
```yaml
UNDERSTANDING_VALIDATION:
  Question: "What exactly does this sub-task require?"
  Evidence: "Clear description of implementation scope"
  
  Question: "What are the acceptance criteria for this sub-task?"
  Evidence: "Specific, measurable completion criteria"
  
  Question: "What tests are needed for this sub-task?"
  Evidence: "Test plan with specific test cases"
```

### Checkpoint 2: Implementation Validation
```yaml
IMPLEMENTATION_VALIDATION:
  Question: "Does the implementation match sub-task requirements?"
  Evidence: "Code review showing alignment with requirements"
  
  Question: "Are coding standards followed?"
  Evidence: "Linting and code quality checks passed"
  
  Question: "Is error handling appropriate?"
  Evidence: "Error scenarios identified and handled"
```

### Checkpoint 3: Testing Validation
```yaml
TESTING_VALIDATION:
  Question: "Are all tests written and passing?"
  Evidence: "Test execution output showing all tests pass"
  
  Question: "Is test coverage adequate?"
  Evidence: "Coverage report showing ≥80% coverage"
  
  Question: "Are there any regressions?"
  Evidence: "Full test suite execution showing no failures"
```

### Checkpoint 4: Completion Validation
```yaml
COMPLETION_VALIDATION:
  Question: "Is the sub-task fully complete?"
  Evidence: "All requirements implemented and tested"
  
  Question: "Is documentation updated?"
  Evidence: "Relevant docs updated with changes"
  
  Question: "Is evidence documented?"
  Evidence: "Debug Log updated with implementation details"
```

## COMPLIANCE MONITORING

### Real-Time Compliance Checks
```yaml
REAL_TIME_MONITORING:
  sub_task_sequence_check:
    - Monitor for sequential sub-task completion
    - Flag any attempts to skip sub-tasks
    - Validate testing evidence for each sub-task
  
  scope_compliance_check:
    - Ensure changes align with current sub-task only
    - Flag scope creep beyond sub-task boundaries
    - Validate no modifications to other tasks
  
  testing_compliance_check:
    - Verify test execution for each sub-task
    - Validate test coverage requirements
    - Check for regression test execution
```

### Compliance Scoring
```yaml
COMPLIANCE_SCORING:
  sub_task_adherence:
    - Sequential completion: "Pass/Fail"
    - Individual testing: "Pass/Fail"
    - Evidence documentation: "Pass/Fail"
    - Scope compliance: "Pass/Fail"
  
  overall_compliance:
    - Excellent: "100% compliance"
    - Good: "≥90% compliance"
    - Needs Improvement: "≥70% compliance"
    - Non-Compliant: "<70% compliance"
```

## ESCALATION PROCEDURES

### Level 1: Warning
```yaml
WARNING_TRIGGERS:
  - Attempting to complete multiple sub-tasks
  - Missing test execution evidence
  - Scope creep detected
  - Insufficient documentation
  
WARNING_ACTIONS:
  - Display compliance reminder
  - Highlight specific violation
  - Provide correction guidance
  - Reset to proper checkpoint
```

### Level 2: Blocking
```yaml
BLOCKING_TRIGGERS:
  - Repeated compliance violations
  - Critical test failures
  - Major scope violations
  - Quality gate failures
  
BLOCKING_ACTIONS:
  - Prevent further progress
  - Require manual validation
  - Escalate to supervisor
  - Document compliance failure
```

### Level 3: Intervention
```yaml
INTERVENTION_TRIGGERS:
  - Persistent non-compliance
  - System integrity risks
  - Quality standard violations
  - Process breakdown
  
INTERVENTION_ACTIONS:
  - Stop all development activity
  - Require process review
  - Implement corrective measures
  - Retrain on compliance requirements
```

## SUCCESS METRICS

### Sub-Task Compliance Metrics
```yaml
COMPLIANCE_METRICS:
  sequential_completion_rate: "> 98%"
  individual_testing_rate: "> 95%"
  evidence_documentation_rate: "> 90%"
  scope_adherence_rate: "> 95%"
  halt_compliance_rate: "> 95%"
```

### Quality Metrics
```yaml
QUALITY_METRICS:
  test_coverage_per_sub_task: "> 80%"
  regression_rate: "< 2%"
  defect_rate_per_sub_task: "< 1%"
  rework_rate: "< 5%"
```

### Efficiency Metrics
```yaml
EFFICIENCY_METRICS:
  sub_task_completion_time: "Within estimates"
  validation_overhead: "< 10% of development time"
  compliance_check_time: "< 30 seconds per sub-task"
  overall_development_velocity: "Maintained or improved"
```

---

**CRITICAL REMINDER:** This checklist MUST be followed for EVERY sub-task. NO exceptions. NO shortcuts. NO bulk completions. Each sub-task individually, with testing, validation, and evidence, followed by HALT for validation.

**Usage:** Execute this checklist for each sub-task before marking it complete [x]
**Enforcement:** Automated compliance monitoring with real-time validation
**Escalation:** Progressive enforcement from warnings to blocking to intervention