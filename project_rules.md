## The Golden Rule: The Three Sources of Truth

**This is the most important rule for all development.**

Before generating any code or making any architectural decision for a given task, you must first mentally re-verify that your approach is fully consistent with the three master documents:

1.  **`project_rules.md` (This Document):** The engineering standards.
2.  **`refactor.md` (The GDD):** The game design and feature specifications.
3.  **`task_list.md`:** The phased construction plan.

All output must be in direct service of the vision and constraints defined in these three files.

# GateGrind Project Rules & Engineering Standards
_Version 4.0 - Unified Discord Bot & Web Application Standards_

**This document defines the engineering philosophy and technical standards for the complete GateGrind ecosystem, including both the Discord bot ("Realm of Shadows") and web application ("GateGrind Web"). It serves as the constitution for all development work across repositories.**

## 0. Multi-Repository Architecture & Integration

### Repository Structure
* **gategrind-api**: Python/FastAPI backend with Discord bot (Pycord) - Core business logic
* **gategrind-web**: TypeScript/Next.js web application - User acquisition & dashboard
* **gategrind-shared**: Shared documentation and API contracts (optional)

### Cross-Repository Coordination Principles
1. **API-First Development**: All features start with API contract definition
2. **Synchronized Releases**: Coordinate releases between repositories
3. **Shared Type System**: Maintain TypeScript types generated from Pydantic models
4. **Unified Testing**: Integration tests cover cross-repository interactions
5. **Documentation Sync**: Keep API documentation accessible to both repositories

### Development Phases Strategy
**V1 (Launch Ready)**: Core functionality for user acquisition and engagement
**V1.5 (Enhanced Experience)**: Advanced features and community focus
**V2 (Production-Grade)**: Real-time capabilities and premium experience

## 1. Core Development Principles

### 1.1 Living Nexus Architecture
The system is designed as a "Living Nexus" - a dynamic, interconnected ecosystem where:
- **Discord Bot**: Primary interaction layer for existing users
- **Web Application**: User acquisition and rich dashboard experience
- **FastAPI Backend**: Centralized business logic and data management
- **Shared Database**: Single source of truth for all user data

### 1.2 API-First Development
- All business logic resides in the FastAPI backend
- Discord bot and web app are presentation layers only
- API contracts defined before implementation
- OpenAPI specifications drive TypeScript type generation

### 1.3 Single-Message UI Philosophy
Every user interaction should provide immediate, clear feedback:
- **Discord**: Rich embeds with clear status and next actions
- **Web**: Responsive components with loading states and error boundaries
- **Consistency**: Unified terminology and visual language across platforms

### 1.4 Progressive Enhancement Strategy
Build features in phases with each phase being production-ready:
- **V1**: Minimum viable features with high quality
- **V1.5**: Enhanced experience with advanced features
- **V2**: Premium features with real-time capabilities

## 2. Technology Stack Standards

### 2.1 Discord Bot Stack
- **Framework**: Pycord (discord.py v2.x)
- **Backend**: FastAPI with async/await
- **Database**: PostgreSQL with AsyncPG
- **Caching**: Redis for session and temporary data
- **Authentication**: JWT tokens for API access
- **Testing**: pytest with async support

### 2.2 Web Application Stack
- **Framework**: Next.js (App Router) with TypeScript
- **Styling**: Tailwind CSS with Shadcn/ui components
- **Animation**: Framer Motion for cinematic sequences
- **State Management**: Zustand (global) + TanStack Query (server state)
- **Authentication**: NextAuth.js with Discord Provider
- **Forms**: React Hook Form with Zod validation
- **Deployment**: Vercel with automated CI/CD

### 2.3 Shared Infrastructure
- **API Documentation**: OpenAPI/Swagger auto-generated from FastAPI
- **Type Generation**: pydantic-to-typescript for shared types
- **Monitoring**: Sentry for error tracking across all services
- **Analytics**: Custom metrics for user engagement and performance

## 3. Core Feature Requirements

### 3.1 User-Centric Design
- **Terminology**: Users are "Ascendants" (not "Operatives")
- **Immersion**: Maintain "shadow realm" theme across all interfaces
- **Personalization**: Greetings format: "Continue your Ascension, Ascendant [Username]"
- **Accessibility**: Support for motion sensitivity, keyboard navigation, screen readers

### 3.2 Autoregulation System
- **Awakening Ritual**: Daily energy assessment with readiness levels
- **Quest Generation**: Personalized based on user's declared energy state
- **Progressive Difficulty**: Automatic adjustment based on completion patterns
- **Recovery Integration**: Built-in rest day recognition and encouragement

### 3.3 Progressive Enhancement
- **Core Functionality**: Works without JavaScript (where possible)
- **Enhanced Experience**: Rich interactions with JavaScript enabled
- **Offline Support**: Service workers for critical functionality
- **Performance**: Sub-3s initial load, sub-2s subsequent loads

## 4. Technical Standards

### 4.1 Panel Registration System (Discord)
All Discord UI components must follow the panel registration pattern:
```python
@panel_manager.register_panel("panel_name")
class PanelClass(BasePanel):
    async def render(self, interaction: discord.Interaction) -> discord.Embed:
        # Implementation
```

### 4.2 Component Architecture (Web)
Follow atomic design principles:
- **Atoms**: Button, Input, Badge (`components/atoms/`)
- **Molecules**: StatCard, QuestItem (`components/molecules/`)
- **Organisms**: Dashboard, CinematicSequence (`components/organisms/`)
- **Templates**: PageLayout, DashboardLayout (`components/templates/`)

### 4.3 Error Handling Standards
- **Graceful Degradation**: System continues functioning with reduced features
- **User-Friendly Messages**: Clear, actionable error messages
- **Comprehensive Logging**: Structured logging for debugging
- **Retry Logic**: Exponential backoff for transient failures

### 4.4 UI/UX Consistency
- **Design System**: Shared color palette, typography, spacing
- **Component Library**: Reusable components across platforms
- **Interaction Patterns**: Consistent button styles, loading states, animations
- **Responsive Design**: Mobile-first approach for web application

## 5. Development Workflow

### 5.1 Git Workflow
- **Branching**: `main` (production) ← `develop` (staging) ← `feature/*`
- **Commits**: Conventional Commits specification
- **Phase Tagging**: Git tags for version milestones (v1.0.0, v1.5.0, v2.0.0)
- **Cross-Repo Coordination**: Synchronized feature branches when needed

### 5.2 Code Quality
- **Linting**: ESLint (TypeScript), flake8 (Python)
- **Formatting**: Prettier (TypeScript), black (Python)
- **Type Safety**: TypeScript strict mode, mypy for Python
- **Testing**: Jest + React Testing Library (web), pytest (backend)

### 5.3 Documentation Standards
- **API Documentation**: Auto-generated from OpenAPI specs
- **Component Documentation**: Storybook for web components
- **Code Comments**: Focus on "why" not "what"
- **README Files**: Clear setup and development instructions

## 6. Security & Performance Standards

### 6.1 Security Requirements
- **Authentication**: Discord OAuth2 with JWT tokens
- **Session Management**: Secure httpOnly cookies with proper expiration
- **CSRF Protection**: Implemented for all state-changing operations
- **Rate Limiting**: Protect against abuse and spam
- **Input Validation**: Zod schemas for all user inputs

### 6.2 Performance Requirements
- **Web Application**: 
  - Initial load < 3s (V1), < 2s (V1.5)
  - Core Web Vitals in "Good" range (V1.5+)
  - Lighthouse score > 90 (V2)
- **Discord Bot**: 
  - Response time < 2s for all interactions
  - 99.9% uptime target
  - Graceful handling of Discord API rate limits

### 6.3 Monitoring & Analytics
- **Error Tracking**: Sentry integration across all services
- **Performance Monitoring**: Custom metrics for key user journeys
- **User Analytics**: Privacy-focused engagement tracking
- **Alerting**: Automated alerts for critical issues

## 7. Discord Bot Integration Architecture

### 7.1 Core Game Mechanics
- **Awakening System**: Daily ritual with readiness level selection
- **Quest Generation**: Tiered quests based on user energy and preferences
- **Stat Progression**: STR, TECH, END with XP-based leveling
- **Dynamic Events**: Shadow Incursions for community engagement

### 7.2 API Integration Points
- **Authentication**: `/api/auth/discord` for OAuth2 flow
- **User Data**: `/api/users/me` for profile and stats
- **Awakening**: `/api/awakening/status` and `/api/awakening/awaken`
- **Quests**: `/api/quests/daily` and `/api/quests/weekly`
- **Logging**: `/api/logging/reps` for workout tracking

### 7.3 Development Mode Support
- **Mock Data**: Returns realistic data when `DEV_MODE=true`
- **Flexible Auth**: Simplified authentication for development
- **Graceful Degradation**: Web app works even if Discord bot is offline

## 8. Success Metrics & KPIs

### 8.1 User Engagement
- **Discord Bot**: Daily active users, quest completion rate, retention
- **Web Application**: Landing page conversion, dashboard engagement, return visits
- **Cross-Platform**: User journey completion from web to Discord

### 8.2 Technical Performance
- **Reliability**: 99.9% uptime across all services
- **Performance**: Meet or exceed Core Web Vitals thresholds
- **Security**: Zero critical security vulnerabilities

### 8.3 Business Metrics
- **User Acquisition**: Conversion rate from web to Discord
- **User Retention**: 7-day and 30-day retention rates
- **Feature Adoption**: Usage rates for key features across platforms

## 9. Phase-Specific Guidelines

### 9.1 V1 (Launch Ready) - Focus Areas
- **Core Functionality**: Essential features only
- **User Acquisition**: Optimized landing page and onboarding
- **Stability**: Rock-solid basic features
- **Performance**: Meet minimum performance thresholds

### 9.2 V1.5 (Enhanced Experience) - Focus Areas
- **Advanced Features**: Rich dashboard, detailed analytics
- **Community Features**: Social elements, leaderboards
- **Performance**: Exceed performance targets
- **Testing**: Comprehensive test coverage

### 9.3 V2 (Production-Grade) - Focus Areas
- **Real-time Features**: WebSocket integration, live updates
- **Advanced Analytics**: Detailed user insights
- **Scalability**: Handle significant user growth
- **Premium Experience**: Industry-leading performance and features

This unified approach ensures consistency across the entire GateGrind ecosystem while maintaining the flexibility to optimize each platform for its specific strengths and user needs.