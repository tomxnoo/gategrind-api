# Realm of Shadows - Project Rules & Development Guidelines
Version: 4.0 | Last Updated: January 2025

## 🎯 CORE DEVELOPMENT RULES

### Rule 1: Documentation First
**Always read PRD.md, planning.md, and project_rules.md before starting any work or task.**
- These documents are the single source of truth for project vision and requirements
- Check task_list.md for current priorities and completion status
- Verify feature specifications before implementation

### Rule 2: Code Understanding
**Always read and understand the existing code before starting any work or task.**
- Review related modules and their dependencies
- Understand the API-first architecture pattern
- Check existing error handling and UI patterns

### Rule 3: Clarification Protocol
**Always ask if unsure about requirements, implementation details, or architectural decisions.**
- Better to clarify than to implement incorrectly
- Document decisions and rationale for future reference

### Rule 4: API Development
**Always read fastAPI.md while working on backend API features.**
- Follow established API patterns and conventions
- Maintain consistency with existing endpoint structures
- Ensure proper error handling and validation

### Rule 5: Task Management
**Follow tasks and rules before starting any work or task.**
- Check current priority levels in task_list.md
- Focus on completing blocked items before new features
- Maintain sequential development approach

### Rule 6: Progress Tracking
**Tick down tasks from task_list.md when updated or completed.**
- Update task status with appropriate markers (✅, 🔄, ❌)
- Document any blockers or issues encountered
- Keep task descriptions current and accurate

## 🏗️ ARCHITECTURAL PRINCIPLES

### The Living Nexus Philosophy
The bot is not a static menu system but a responsive, intelligent companion that:
- Reacts dynamically to user state and actions
- Creates personalized, meaningful interactions
- Maintains immersive "shadow assassin" theming throughout
- Supports the user's unique high-frequency training methodology

### API-First Architecture
**All logic must live in the FastAPI backend:**
- Discord bot is purely a UI client making HTTP requests
- Database operations handled exclusively through API endpoints
- Redis caching managed at the API layer
- Authentication via JWT tokens

### Single-Message UI Constraint
**All user interactions contained within persistent ephemeral Discord messages:**
- Navigation through buttons and dropdown menus only
- Panel-based system with universal registration pattern
- Consistent header/sub-header structure across all panels
- Universal loading animations for all interactions

## 🎮 CORE FEATURE REQUIREMENTS

### User-Centric Design
**Built for a specific user profile:**
- 3-shift rotation worker (06-14, 14-22, 22-06)
- High-frequency "Grease the Groove" training style
- Autoregulation-based approach (energy-dependent intensity)
- V-taper physique goal (wide shoulders/back, narrow waist)
- Gaming-oriented mindset requiring engaging gamification

### Autoregulation Support
**The system must enhance, not fight, the user's natural training instincts:**
- Daily "Awakening" ritual for readiness assessment
- Quest difficulty scaling based on declared energy level
- Support for distributed, short training sessions
- Flexible timing without rigid scheduling

### Progressive Enhancement
**Features must build upon a stable foundation:**
- Core gameplay loop must be rock-solid before adding complexity
- Each new feature should integrate seamlessly with existing systems
- Maintain backward compatibility during development
- Test thoroughly before moving to next feature

## 🔧 TECHNICAL STANDARDS

### Panel Registration Pattern
**All UI panels must follow the established registration system:**
```python
from shared.utils.panel_registry import register

@register
class MyPanel:
    key = "unique_key"        # Panel switcher identifier
    label = "Display Name"    # Dropdown display text
    emoji = "🎯"              # Dropdown icon
    
    @staticmethod
    async def render_embed(bot, user, **kwargs):
        # Return discord.Embed with universal headers
        
    @staticmethod
    async def build_view(bot, user, **kwargs):
        # Return discord.ui.View with error handling
```

### Error Handling Standards
**Universal error handling across all components:**
- Use `@handle_panel_errors` decorator for all panel methods
- Implement graceful degradation for API failures
- Provide meaningful user feedback for all error states
- Log errors with appropriate context for debugging

### UI/UX Consistency
**Maintain visual and interaction consistency:**
- Universal header + sub-header for all panels
- Consistent loading animations for all buttons
- Thematic "shadow assassin" styling throughout
- Responsive feedback for all user actions

## 📋 DEVELOPMENT WORKFLOW

### Priority Management
**Current Focus Areas (in order):**
1. **CRITICAL**: Fix awakening data synchronization issues
2. **HIGH**: Implement Shadow Labyrinths & Keys system
3. **MEDIUM**: Enhance History Panel ("Shadow Archive")
4. **LOW**: Future features (achievements, social systems)

### Quality Assurance
**Before marking any task as complete:**
- Test all user interaction flows
- Verify API endpoint functionality
- Check error handling edge cases
- Ensure UI consistency with existing panels
- Update documentation if needed

### Code Organization
**Maintain clean, modular structure:**
- Features organized by domain (awakening, quests, incursions, etc.)
- Logic separated from UI components
- Shared utilities in common modules
- Clear separation between API and Discord client code

## 🎯 SUCCESS METRICS

### Daily Driver Milestone
**The ultimate goal is a bot that the user actually uses daily:**
- Stable, bug-free core functionality
- Engaging, motivating user experience
- Seamless integration with existing workout routine
- Reliable data tracking and progression systems

### Technical Excellence
**Maintain high code quality standards:**
- Comprehensive error handling
- Efficient database operations
- Responsive UI interactions
- Scalable architecture patterns

### User Experience
**Every interaction should feel alive and meaningful:**
- Immediate feedback for all actions
- Contextual, intelligent responses
- Immersive thematic presentation
- Intuitive navigation and discovery

---

*Remember: This project is built for one specific user with unique needs. Every decision should be evaluated against whether it enhances their daily training experience and supports their specific goals and constraints.*