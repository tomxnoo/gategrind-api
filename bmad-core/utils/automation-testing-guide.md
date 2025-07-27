# Automation Testing Guide

## 🎯 **Testing the bmad-core Automation System**

This guide explains how to verify that your automated workspace context loading and agent compliance enforcement is working correctly.

## 📋 **Current System Status**

### ✅ **Workspace Infrastructure (JS Utilities)**
- **Status**: ✅ HEALTHY - Already initialized and running
- **Active Sessions**: 2 sessions detected
- **Structure**: All directories present and healthy
- **Scripts**: Using `workspace-utils-fixed/` (correct version)

### ✅ **bmad-core Automation System**
- **Status**: ✅ DEPLOYED - All components created and configured
- **Auto-Context Loading**: Ready for agent activation
- **Workflow Enforcement**: Enhanced dev agent with strict sub-task rules
- **Compliance Monitoring**: Real-time monitoring system ready

## 🧪 **Testing Procedures**

### **1. Test Auto-Context Loading**

**What to Test**: Verify agents automatically load workspace context without manual prompting.

**How to Test**:
```bash
# Activate the enhanced dev agent and observe if it:
# ✅ Automatically mentions workspace context
# ✅ References current handoffs/progress
# ✅ Shows awareness of project state
# ✅ No manual context prompting needed
```

**Expected Behavior**:
- Agent immediately shows workspace awareness
- Mentions current project state, handoffs, progress
- No need to manually provide context
- References architecture and technology stack

### **2. Test Workflow Enforcement**

**What to Test**: Verify dev agent follows strict sub-task completion protocol.

**How to Test**:
```bash
# Give dev agent a story with multiple sub-tasks
# Observe if it:
# ✅ Completes ONE sub-task at a time
# ✅ Tests each sub-task individually
# ✅ Documents evidence for each sub-task
# ✅ HALTs after each sub-task for validation
# ❌ Does NOT bulk complete multiple tasks
```

**Expected Behavior**:
- Completes sub-task 1 → Tests → Documents → Marks [x] → HALTS
- Waits for validation before proceeding to sub-task 2
- Never completes multiple sub-tasks in one response

### **3. Test Compliance Monitoring**

**What to Test**: Verify the system catches and prevents rule violations.

**How to Test**:
```bash
# Try to get dev agent to:
# - Skip testing a sub-task
# - Complete multiple sub-tasks at once
# - Skip documentation
# 
# System should:
# ✅ Block these actions
# ✅ Provide warnings
# ✅ Enforce compliance
```

## 🔍 **Verification Checklist**

### **Auto-Context Loading Verification**
- [ ] Agent shows immediate workspace awareness
- [ ] References current handoffs without prompting
- [ ] Mentions project progress and quality status
- [ ] Shows architecture and tech stack knowledge
- [ ] No manual context requests needed

### **Workflow Enforcement Verification**
- [ ] Dev agent completes ONE sub-task at a time
- [ ] Tests each sub-task individually
- [ ] Documents implementation evidence
- [ ] HALTs after each sub-task completion
- [ ] Blocks bulk task completion attempts

### **Compliance Monitoring Verification**
- [ ] System detects rule violations
- [ ] Provides compliance warnings
- [ ] Blocks non-compliant actions
- [ ] Tracks compliance scoring
- [ ] Escalates repeated violations

## 🚀 **Quick Test Commands**

### **Test Workspace Status**
```bash
npm run workspace-status
# Should show healthy workspace with active sessions
```

### **Test Context Loading**
```bash
# Activate dev agent and ask: "What's the current project state?"
# Should automatically provide comprehensive context
```

### **Test Workflow Enforcement**
```bash
# Give dev agent a multi-sub-task story
# Should complete only first sub-task and HALT
```

## 🎯 **Success Indicators**

### **🟢 System Working Correctly**
- Agents show immediate workspace awareness
- Dev agent follows strict sub-task protocol
- No manual context prompting needed
- Compliance violations are blocked
- Quality gates are enforced

### **🔴 System Needs Attention**
- Agents ask for manual context
- Dev agent completes multiple sub-tasks at once
- No testing between sub-tasks
- Bulk completion allowed
- Rule violations not caught

## 📊 **Monitoring Dashboard**

### **Key Metrics to Watch**
- **Context Loading Time**: <2 seconds for immediate context
- **Sub-task Compliance**: 100% individual completion rate
- **Testing Coverage**: 100% sub-tasks tested before marking [x]
- **HALT Compliance**: 100% stops after each sub-task
- **Rule Violations**: 0 successful violations

## 🔧 **Troubleshooting**

### **If Auto-Context Loading Fails**
1. Check `core-config.yaml` devLoadAlwaysFiles section
2. Verify bmad-core files are accessible
3. Check workspace structure with `npm run workspace-status`

### **If Workflow Enforcement Fails**
1. Verify enhanced dev agent configuration is loaded
2. Check compliance monitor is active
3. Review agent activation instructions

### **If Compliance Monitoring Fails**
1. Check real-time monitoring hooks
2. Verify validation checkpoints
3. Review escalation procedures

## 🎉 **Expected Results**

With the automation system working correctly, you should see:

1. **Zero Manual Context Prompting** - Agents automatically aware
2. **Perfect Sub-task Compliance** - One at a time, tested, documented
3. **Quality Enforcement** - All gates enforced automatically
4. **Productivity Boost** - Faster development with higher quality
5. **Zero Agent "Rampage"** - Controlled, methodical execution

The system transforms agent behavior from chaotic bulk completion to methodical, quality-focused execution! 🚀