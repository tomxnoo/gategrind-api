# BMad-Core Directory Cleanup Plan

## Issue Summary
Multiple bmad-core directories causing random agent loading behavior:
- `/.bmad-core/` (V4 standard, complete config)
- `/bmad-core/` (incomplete, outdated config)  
- `/dist/agents/` (build artifacts)

## Current State Analysis

### /.bmad-core/ (KEEP - Primary)
- ✅ Complete 34-line core-config.yaml
- ✅ Has install-manifest.yaml (official V4)
- ✅ Comprehensive devLoadAlwaysFiles (11 files)
- ✅ Includes smLoadAlwaysFiles section
- ✅ References correct PRD: "docs/greenfield-prd.md"

### /bmad-core/ (REMOVE - Outdated)
- ❌ Minimal 20-line core-config.yaml
- ❌ Missing install-manifest.yaml
- ❌ Limited devLoadAlwaysFiles (3 files only)
- ❌ No smLoadAlwaysFiles section
- ❌ References outdated PRD: "docs/prd.md"

### /dist/agents/ (EVALUATE - Build Artifacts)
- Contains .txt versions of agent files
- Likely build/distribution artifacts
- May be safe to remove if not used by build process

## Cleanup Actions

### Phase 1: Backup Current State
1. Create backup of /bmad-core/ directory
2. Document any differences in agent files
3. Verify /.bmad-core/ has all necessary files

### Phase 2: Remove Duplicates
1. Remove /bmad-core/ directory (after backup)
2. Evaluate /dist/agents/ usage and remove if not needed
3. Update any hardcoded references to point to /.bmad-core/

### Phase 3: Verification
1. Test agent loading consistency
2. Verify all context files load properly
3. Confirm no broken references

## Expected Outcome
- Single source of truth: /.bmad-core/
- Consistent agent behavior
- Full context loading every time
- No more random configuration loading

## Risk Mitigation
- Full backup before any deletions
- Incremental testing after each change
- Ability to rollback if issues arise