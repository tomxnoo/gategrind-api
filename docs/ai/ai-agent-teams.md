# AI Agent Teams

## Multi-Agent Collaboration Framework

### Team Structure Overview
The BMad-Method framework employs specialized AI agents working in coordinated teams to deliver complex software development projects with zero-defect standards.

### Core Agent Roles

#### 🏗️ **Story Manager (Alex)**
- **Primary Role**: Epic and story planning, breakdown, and coordination
- **Responsibilities**:
  - Story analysis and complexity assessment
  - Task and subtask breakdown
  - Acceptance criteria definition
  - Agent handoff coordination
  - Progress tracking and validation
- **Handoff Triggers**: Story draft complete, technical review needed
- **Quality Gates**: Story completeness, acceptance criteria clarity, task breakdown

#### 💻 **Enhanced Developer (James)**
- **Primary Role**: Complex story implementation with zero-defect standards
- **Responsibilities**:
  - Technical architecture review
  - Implementation feasibility assessment
  - Code development and testing
  - Security and performance validation
  - V2 component integration
- **Handoff Triggers**: Implementation complete, QA review needed
- **Quality Gates**: Code quality, test coverage ≥80%, performance benchmarks

#### 🔍 **Quality Assurance Agent**
- **Primary Role**: Comprehensive testing and quality validation
- **Responsibilities**:
  - Test strategy development
  - Edge case identification
  - Performance testing
  - Security validation
  - Regression testing
- **Handoff Triggers**: Quality validation complete, ready for review
- **Quality Gates**: Test coverage, performance metrics, security scan

#### 📋 **Product Owner Agent**
- **Primary Role**: Requirements definition and acceptance validation
- **Responsibilities**:
  - Business requirement analysis
  - User story validation
  - Acceptance criteria review
  - Stakeholder communication
  - Final acceptance approval
- **Handoff Triggers**: Requirements clarified, development ready
- **Quality Gates**: Requirement completeness, business value validation

### Team Collaboration Patterns

#### Sequential Handoff Pattern
```
Story Manager → Developer → QA → Story Manager → Product Owner
```
- **Use Case**: Standard story development workflow
- **Validation**: Each agent completes quality gates before handoff
- **Control**: Explicit user confirmation for each transition

#### Parallel Collaboration Pattern
```
Story Manager ↔ Developer ↔ QA
```
- **Use Case**: Complex stories requiring iterative refinement
- **Validation**: Continuous integration and validation
- **Control**: Real-time collaboration with shared context

#### Emergency Response Pattern
```
Any Agent → Developer → QA → Immediate Deployment
```
- **Use Case**: Critical bug fixes or security patches
- **Validation**: Accelerated but comprehensive testing
- **Control**: Elevated permissions for rapid response

### Agent Communication Protocols

#### Handoff Announcements
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
```

#### Status Synchronization
- **Real-time Updates**: Shared workspace context through `.workspace` directory
- **Progress Tracking**: Continuous story status and completion updates
- **Quality Metrics**: Shared quality scoring and validation results
- **Decision Logging**: Architectural and technical decisions preserved

### Team Quality Standards

#### Collective Responsibility
- **Zero-Defect Commitment**: All agents maintain zero-defect standards
- **Continuous Validation**: Each agent validates previous work
- **Knowledge Sharing**: Context and decisions shared across team
- **Collective Ownership**: Team responsibility for final quality

#### Cross-Agent Validation
- **Technical Review**: Developer validates Story Manager's technical feasibility
- **Quality Review**: QA validates Developer's implementation quality
- **Business Review**: Product Owner validates business value delivery
- **Continuous Feedback**: Real-time feedback and course correction

### Specialized Team Configurations

#### **Full-Stack Development Team**
- **Composition**: Story Manager + Enhanced Developer + QA
- **Focus**: Complete feature development with comprehensive testing
- **Use Case**: Major feature implementation, system integration

#### **Quality-First Team**
- **Composition**: Enhanced Developer + QA + Security Specialist
- **Focus**: Zero-defect implementation with security emphasis
- **Use Case**: Critical system components, security-sensitive features

#### **Rapid Response Team**
- **Composition**: Enhanced Developer + QA (accelerated protocols)
- **Focus**: Emergency fixes with maintained quality standards
- **Use Case**: Production issues, critical bug fixes

### Team Performance Metrics

#### Velocity Metrics
- **Story Completion Rate**: Stories completed per sprint
- **Quality Score**: Average quality score across completed stories
- **Handoff Efficiency**: Time between agent transitions
- **Rework Rate**: Stories requiring significant revision

#### Quality Metrics
- **Defect Rate**: Bugs found in production per story
- **Test Coverage**: Average test coverage across all implementations
- **Performance Compliance**: Stories meeting performance benchmarks
- **Security Compliance**: Stories passing security validation

#### Collaboration Metrics
- **Handoff Success Rate**: Successful agent transitions without rollback
- **Communication Clarity**: Handoff package completeness scores
- **Context Preservation**: Information retention across handoffs
- **Decision Traceability**: Architectural decisions properly documented

### Team Evolution and Learning

#### Continuous Improvement
- **Retrospective Analysis**: Regular team performance review
- **Process Refinement**: Workflow optimization based on metrics
- **Knowledge Base Growth**: Expanding shared context and patterns
- **Tool Enhancement**: Improving automation and validation tools

#### Adaptive Specialization
- **Role Evolution**: Agents adapt to project-specific needs
- **Skill Development**: Enhanced capabilities through experience
- **Pattern Recognition**: Improved efficiency through learned patterns
- **Context Optimization**: Better context loading and management

### Integration with BMad-Core System

#### Automated Team Coordination
- **Workflow Enforcement**: Automated handoff validation and enforcement
- **Context Synchronization**: Real-time team context sharing
- **Quality Gate Automation**: Automated quality validation and blocking
- **Performance Monitoring**: Team performance tracking and optimization

#### Enhanced Collaboration Tools
- **Shared Workspace**: `.workspace` directory for team coordination
- **Context Management**: `workspace-utils-enhanced` for team context
- **Compliance Monitoring**: Real-time workflow compliance enforcement
- **Decision Tracking**: Comprehensive decision logging and retrieval