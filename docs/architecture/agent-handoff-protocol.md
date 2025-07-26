# Agent Handoff Protocol

## Overview
Explicit commands and validation checkpoints for multi-agent workflow transitions to ensure quality and user control.

## Handoff Commands

### **Primary Handoff Commands**
```
*switch-to-dev     # Request Developer review with validation checklist
*switch-to-qa      # Request QA review with quality gates
*switch-to-sm      # Return to Scrum Master for revision
*approve-story     # Final approval and status change
*request-clarification  # Ask for user input on ambiguous items
```

### **Validation Commands**
```
*validate-handoff  # Check if current agent completed required tasks
*review-checklist  # Display agent-specific completion checklist
*force-handoff     # Override validation (with user confirmation)
*rollback-agent    # Return to previous agent in workflow
```

## Agent Transition Validation

### **SM → Dev Handoff Checklist**
Before switching to Developer, SM must confirm:
- [ ] All acceptance criteria clearly defined and measurable
- [ ] Technical dependencies identified and documented
- [ ] Architecture context provided (V2 patterns specified)
- [ ] Performance requirements specified
- [ ] Security considerations outlined
- [ ] Database schema requirements defined
- [ ] Integration points with existing systems mapped

**Handoff Command**: `*switch-to-dev`
**Validation**: Automatic checklist verification before transition

### **Dev → QA Handoff Checklist**
Before switching to QA, Dev must confirm:
- [ ] Technical implementation plan complete and feasible
- [ ] Security considerations documented with specific patterns
- [ ] Error handling patterns defined with custom exceptions
- [ ] Database schema validated with proper indexing
- [ ] Performance optimization strategies specified
- [ ] Integration testing approach outlined
- [ ] Code quality standards defined (coverage, linting)

**Handoff Command**: `*switch-to-qa`
**Validation**: Technical completeness check before transition

### **QA → SM Handoff Checklist**
Before returning to SM, QA must confirm:
- [ ] Test coverage requirements specified (minimum 80%)
- [ ] Edge cases and error scenarios identified
- [ ] Performance testing requirements defined
- [ ] Integration points validated for testability
- [ ] Load testing scenarios specified
- [ ] Security testing approach outlined
- [ ] Regression testing strategy defined

**Handoff Command**: `*switch-to-sm`
**Validation**: Quality assurance completeness check

## Enhanced Validation Gates

### **Technical Quality Gates (Dev)**
```yaml
technical_validation:
  architecture_compliance:
    - v2_patterns_used: true
    - hexagonal_architecture: true
    - dependency_injection: true
  
  implementation_feasibility:
    - complexity_assessed: true
    - effort_estimated: true
    - dependencies_mapped: true
  
  security_standards:
    - authentication_defined: true
    - authorization_patterns: true
    - input_validation: true
    - error_handling: true
  
  performance_considerations:
    - caching_strategy: true
    - database_optimization: true
    - async_patterns: true
```

### **Quality Assurance Gates (QA)**
```yaml
quality_validation:
  testability:
    - unit_test_strategy: true
    - integration_test_plan: true
    - test_coverage_target: ">=80%"
  
  edge_cases:
    - error_scenarios: true
    - boundary_conditions: true
    - concurrent_access: true
  
  performance_testing:
    - load_testing_plan: true
    - stress_testing_scenarios: true
    - performance_benchmarks: true
  
  security_testing:
    - vulnerability_assessment: true
    - penetration_testing_plan: true
    - data_protection_validation: true
```

## Automated Validation Checks

### **Pre-Handoff Validation Script**
```python
def validate_handoff(current_agent: str, target_agent: str, story_data: dict) -> bool:
    """Validate if handoff requirements are met"""
    
    validation_rules = {
        "sm_to_dev": [
            "acceptance_criteria_defined",
            "technical_dependencies_mapped", 
            "architecture_context_provided"
        ],
        "dev_to_qa": [
            "implementation_plan_complete",
            "security_patterns_defined",
            "error_handling_specified"
        ],
        "qa_to_sm": [
            "test_coverage_specified",
            "edge_cases_identified",
            "performance_testing_defined"
        ]
    }
    
    handoff_key = f"{current_agent}_to_{target_agent}"
    required_checks = validation_rules.get(handoff_key, [])
    
    for check in required_checks:
        if not validate_requirement(story_data, check):
            return False
    
    return True
```

## User Confirmation Protocol

### **Explicit User Prompts**
When agents need to transition, they will:

1. **Announce the transition**:
   ```
   🔄 **Agent Transition Required**
   Current: Story Manager (Alex)
   Next: Developer (James)
   Reason: Story draft complete, technical review needed
   
   Quality Gate Status: ✅ PASSED (Score: 87/100)
   - Story completeness: ✅
   - Acceptance criteria: ✅ (5 criteria defined)
   - Task breakdown: ✅ (8 tasks, 32 subtasks)
   - Technical context: ✅
   
   Would you like me to proceed with the handoff? (y/n)
   Or type '*validate-handoff' to see detailed validation results
   ```

2. **Wait for user confirmation** before switching
3. **Provide transition summary** when confirmed
4. **Show quality validation results** if requested

### **Enhanced Transition Announcements**
```
🔄 **AGENT HANDOFF INITIATED**

FROM: Story Manager (Alex) ➜ TO: Developer (James)
TRIGGER: Story draft completion
VALIDATION: ✅ Quality Gate Passed (92/100)

📋 HANDOFF PACKAGE:
✅ Story: 5.2 Dungeon System
✅ Status: Draft → Under Technical Review  
✅ Quality Score: 92/100
✅ Acceptance Criteria: 6 defined
✅ Tasks: 8 tasks, 32 subtasks
✅ Technical Context: Complete
✅ Dependencies: Identified

🎯 NEXT AGENT FOCUS:
- Technical architecture review
- Implementation feasibility assessment  
- Security and performance validation
- Code quality standards verification

Proceed with handoff? (y/n) or '*validate-handoff' for details
```

When agent requests handoff:

```
🔄 AGENT HANDOFF REQUEST

Current Agent: Story Manager (SM)
Requested Agent: Developer (Dev)
Story: 5.2 Dungeon System

✅ Handoff Validation:
- [✅] Acceptance criteria defined
- [✅] Technical dependencies mapped  
- [✅] Architecture context provided
- [❌] Performance requirements specified

❌ HANDOFF BLOCKED: Missing performance requirements

Options:
1. Complete missing requirements
2. Request clarification from user
3. Force handoff (not recommended)

Please choose: [1/2/3]
```

### **Successful Handoff Confirmation**
```
✅ HANDOFF APPROVED

Transitioning from: Story Manager (SM)
Transitioning to: Developer (Dev)
Story: 5.2 Dungeon System

All validation checks passed. Developer will now review technical implementation approach.

Continue? [Y/n]
```

## Quality Improvement Metrics

### **Handoff Quality Tracking**
```yaml
metrics:
  handoff_success_rate: 
    target: ">95%"
    measurement: "successful_handoffs / total_handoff_attempts"
  
  validation_failure_rate:
    target: "<5%"
    measurement: "failed_validations / total_handoff_attempts"
  
  revision_cycles:
    target: "<=2"
    measurement: "average_revision_cycles_per_story"
  
  user_intervention_rate:
    target: "<10%"
    measurement: "manual_overrides / total_handoffs"
```

### **Continuous Improvement Process**
1. **Weekly Review**: Analyze handoff metrics and failure points
2. **Monthly Optimization**: Update validation rules based on patterns
3. **Quarterly Enhancement**: Refine agent responsibilities and checklists
4. **User Feedback Integration**: Incorporate user preferences for handoff style

## Implementation Commands

### **For Immediate Implementation**
1. Add handoff commands to each agent's command list
2. Implement validation checklists in agent workflows
3. Create user confirmation prompts for transitions
4. Add metrics tracking for handoff quality

### **For Enhanced User Control**
```
*set-handoff-mode [automatic|manual|hybrid]
  - automatic: Agents transition when validation passes
  - manual: User confirms every transition
  - hybrid: Auto for successful validations, manual for failures

*customize-validation [strict|standard|relaxed]
  - strict: All checklist items required
  - standard: 80% of checklist items required
  - relaxed: Core items only required
```

This protocol ensures you have explicit control over agent transitions while maintaining quality standards and preventing the "silent switching" issue you experienced.