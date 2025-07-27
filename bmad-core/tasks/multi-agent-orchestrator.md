# Multi-Agent Story Creation & Enhancement Orchestrator

## Purpose
Execute collaborative story creation workflow where SM, Dev, and QA agents work together to create, review, and enhance a story draft before final approval.

## SEQUENTIAL Task Execution (Do not proceed until current Task is complete)

### 1. Initialize Story Creation Workflow
- Display: "🚀 **MULTI-AGENT STORY CREATION INITIATED**"
- Display: "This workflow will create an enhanced story through: SM Draft → Dev Review → QA Review → SM Review → Dev Final Check → QA Final Check → Approval"
- Set workflow state: `story-drafting`
- Create workflow tracking in story metadata

### 2. Phase 1: SM Initial Story Draft
- Display: "📝 **PHASE 1: SM STORY DRAFTING**"
- Display: "Scrum Master creating initial story draft..."
- Execute story drafting workflow (create-next-story.md)
- Create comprehensive story with all required sections
- Display: "✅ Initial story draft complete"
- **AUTOMATIC HANDOFF TO DEV**
- Execute `*switch-to-dev` command automatically
- Display: "🔄 Transitioning to Developer for review and enhancement..."

### 3. Phase 2: Dev Review & Enhancement
- Display: "💻 **PHASE 2: DEV REVIEW & ENHANCEMENT**"
- Display: "Developer reviewing story and adding technical enhancements..."
- **AUTOMATIC EXECUTION**:
  - Review story for technical completeness
  - Add/enhance technical implementation details
  - Improve dev notes and architecture context
  - Enhance task definitions and acceptance criteria
  - Add missing technical considerations
- Display: "✅ Dev review and enhancements complete"
- **AUTOMATIC HANDOFF TO QA**
- Execute `*switch-to-qa` command automatically
- Display: "🔄 Transitioning to QA for review and enhancement..."

### 4. Phase 3: QA Review & Enhancement
- Display: "🧪 **PHASE 3: QA REVIEW & ENHANCEMENT**"
- Display: "QA reviewing story and adding testing enhancements..."
- **AUTOMATIC EXECUTION**:
  - Review story for testability and quality
  - Add/enhance testing requirements and scenarios
  - Improve acceptance criteria for testability
  - Add edge cases and validation requirements
  - Enhance quality assurance considerations
- Display: "✅ QA review and enhancements complete"
- **AUTOMATIC HANDOFF BACK TO SM**
- Execute `*switch-to-sm` command automatically
- Display: "🔄 Transitioning back to Scrum Master for review..."

### 5. Phase 4: SM Review & Integration
- Display: "📊 **PHASE 4: SM REVIEW & INTEGRATION**"
- Display: "Scrum Master reviewing all enhancements and integrating feedback..."
- **AUTOMATIC EXECUTION**:
  - Review all Dev and QA enhancements
  - Integrate feedback into cohesive story
  - Ensure story completeness and consistency
  - Validate all sections are properly enhanced
  - Perform final story quality check
- Display: "✅ SM integration and review complete"
- **AUTOMATIC HANDOFF TO DEV FOR FINAL CHECK**
- Execute `*switch-to-dev` command automatically
- Display: "🔄 Transitioning to Developer for final technical check..."

### 6. Phase 5: Dev Final Technical Check
- Display: "🔍 **PHASE 5: DEV FINAL TECHNICAL CHECK**"
- Display: "Developer performing final technical validation..."
- **AUTOMATIC EXECUTION**:
  - Validate technical completeness
  - Check if anything is missing from implementation perspective
  - Verify all technical requirements are clear
  - Confirm story is ready for implementation
- **CONDITIONAL DECISION**:
  - If technical check passes:
    - Display: "✅ **DEV FINAL CHECK: APPROVED** - Story is technically complete"
    - **AUTOMATIC HANDOFF TO QA FOR FINAL CHECK**
    - Execute `*switch-to-qa` command automatically
    - Display: "🔄 Transitioning to QA for final quality check..."
  - If issues found:
    - Display: "❌ **DEV FINAL CHECK: ISSUES FOUND** - Requires revision"
    - Return to Phase 4 (SM Review & Integration)

### 7. Phase 6: QA Final Quality Check
- Display: "✅ **PHASE 6: QA FINAL QUALITY CHECK**"
- Display: "QA performing final quality validation..."
- **AUTOMATIC EXECUTION**:
  - Validate story quality and completeness
  - Check testability and acceptance criteria
  - Verify all quality requirements are met
  - Confirm story is ready for implementation
- **CONDITIONAL DECISION**:
  - If quality check passes:
    - Display: "✅ **QA FINAL CHECK: APPROVED** - Story meets all quality standards"
    - **AUTOMATIC HANDOFF TO USER**
    - Execute `*switch-to-sm` command automatically
    - Display: "🔄 Transitioning back to Scrum Master for final handoff..."
    - Proceed to Phase 7
  - If issues found:
    - Display: "❌ **QA FINAL CHECK: ISSUES FOUND** - Requires revision"
    - Return to Phase 4 (SM Review & Integration)

### 8. Phase 7: Final Story Approval
- Display: "🎉 **PHASE 7: ENHANCED STORY READY FOR APPROVAL**"
- Display: "📋 **STORY CREATION COMPLETE** - Enhanced story ready for your review"
- Display story summary with all enhancements
- **PAUSE FOR USER FINAL APPROVAL**:
  - Display: "Commands available:"
  - Display: "  • Type 'approve' to approve the enhanced story"
  - Display: "  • Type 'review' to see detailed story with all enhancements"
  - Display: "  • Type 'revise' to request additional changes"
- Wait for user input

### 9. Final Completion
- When user types 'approve':
  - Display: "✅ **MULTI-AGENT STORY CREATION COMPLETE!**"
  - Mark story as approved and ready for implementation
  - Update workflow state: `story-approved`
  - Display: "📊 Story Creation Summary:"
  - Display: "  • SM Initial Draft: COMPLETE ✓"
  - Display: "  • Dev Enhancements: COMPLETE ✓"
  - Display: "  • QA Enhancements: COMPLETE ✓"
  - Display: "  • SM Integration: COMPLETE ✓"
  - Display: "  • Dev Final Check: APPROVED ✓"
  - Display: "  • QA Final Check: APPROVED ✓"
  - Display: "  • Story Status: APPROVED & READY FOR IMPLEMENTATION 🚀"

## User Interaction Commands
- `approve` - Final approval of enhanced story
- `revise` - Request additional changes to story
- `review` - Show detailed enhanced story content
- `debug` - Show debugging information
- `abort` - Cancel story creation workflow
- `status` - Show current workflow state and progress

## Workflow Automation Rules
- **FULLY AUTOMATED COLLABORATION**: All agent transitions happen automatically
- **ENHANCEMENT FOCUSED**: Each agent adds their expertise to improve the story
- **QUALITY GATES**: Dev and QA perform final validation checks
- **REVISION LOOPS**: Failed checks automatically trigger revision cycles
- **USER APPROVAL ONLY AT END**: You only review and approve the final enhanced story

## Error Handling
- Quality gate failures: Pause and show specific issues
- Agent transition failures: Halt and request manual intervention
- Test failures: Pause for debugging before continuing
- User abort: Confirm cancellation and preserve workflow state

## Success Criteria
- All phases completed with user approval
- All quality gates passed
- Story marked as complete and approved
- Full audit trail maintained