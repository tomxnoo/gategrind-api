# GateGrind Web Application: Project Rules & Engineering Standards
_Version 2.0 - Last Updated: 2025-01-18_

**This document defines the engineering philosophy and technical standards for the GateGrind web application. It is the constitution for all development work. The goal is not just to build features, but to build them correctly with a focus on quality, performance, and long-term maintainability.**

## 0. Multi-Repo Architecture & Phased Development

### Repository Structure
* **gategrind-api**: Python/FastAPI backend with Discord bot (Pycord)
* **gategrind-web**: TypeScript/Next.js web application (this repository)

### Type Sharing Strategy
Since direct type sharing between Python and TypeScript is not possible, we use:
* **OpenAPI Specification**: Auto-generated from FastAPI for API contracts
* **pydantic-to-typescript**: Convert Pydantic models to TypeScript interfaces
* **Shared Documentation**: Maintain synchronized API documentation

### Phased Development Approach
**V1 (Launch Ready)**: Core functionality for user acquisition
**V1.5 (First Major Update)**: Enhanced features and optimizations  
**V2 (Production-Grade)**: Advanced features and real-time capabilities

*All features are categorized by phase to prevent scope creep and ensure focused development.*

## 1. Core Principles

1.  **Vision First, Code Second:** All development must serve the core vision of an immersive, high-quality, and performant user experience. No feature should compromise the brand's aesthetic or performance goals.
2.  **API-First Architecture:** The web app is a **client** to the FastAPI backend. It should be treated as such. All business logic and data manipulation must remain in the backend. The web app is responsible for presentation, user interaction, and state management only.
3.  **Component-Based Architecture:** The UI will be constructed from small, reusable, and single-purpose components. We favor composition over inheritance and complexity.
4.  **Mobile-First Responsive Design:** All components and pages must be designed for mobile screens first, then scaled up to tablet and desktop. This is non-negotiable.
5.  **Performance is a Feature:** The application must be fast. This includes fast initial loads, fast transitions, and smooth animations. Performance budgets will be considered, and optimization is a continuous process, not an afterthought.
6.  **Phased Excellence:** Each development phase must be production-ready. No "placeholder" or "temporary" solutions that compromise quality.

## 2. Technology Stack (The "GateGrind Starter Pack")

This stack is definitive and should not be deviated from without a formal decision.

* **Framework:** Next.js (App Router)
* **Language:** TypeScript (`strict` mode enabled)
* **Styling:** Tailwind CSS
* **UI Components:** Shadcn/ui
* **Animation:** Framer Motion
* **State Management:** Zustand (for global state) + TanStack Query (for server state)
* **Form Handling:** React Hook Form with Zod validation
* **Authentication:** NextAuth.js with Discord Provider
* **Deployment:** Vercel
* **Version Control:** Git, hosted on GitHub

### V1 Stack Priorities
Focus on core technologies only. Advanced tooling (Storybook, Chromatic) deferred to V1.5.

## 3. Code Quality & Organization

* **Linting & Formatting:** `ESLint` and `Prettier` will be configured and enforced. Code must be free of linting errors and automatically formatted on save.
* **TypeScript Strictness:** All new code must be strongly typed. The use of `any` is forbidden except in rare, well-documented cases.
* **Directory Structure:** Follow the standard Next.js App Router conventions. Reusable components will live in `/components`. Utility functions will live in `/lib` or `/utils`.
* **Component Architecture:** Follow atomic design principles:
    * `components/atoms/` - Button, Input, Badge
    * `components/molecules/` - StatCard, QuestItem
    * `components/organisms/` - Dashboard, CinematicSequence
    * `components/templates/` - PageLayout, DashboardLayout
* **API Client Layer:** Mirror FastAPI endpoints with typed client functions
* **Naming Conventions:**
    * Components: `PascalCase` (e.g., `StatDisplayCard.tsx`)
    * Files (non-components): `kebab-case` (e.g., `api-helpers.ts`)
    * Variables & Functions: `camelCase`
    * Types & Interfaces: `PascalCase` (e.g., `type UserProfile = { ... }`)
* **Environment Variables:** All secret keys (API keys, Discord secrets) **must** be managed through environment variables (`.env.local`) and never hard-coded. Use the `NEXT_PUBLIC_` prefix only for variables that need to be exposed to the browser.

## 4. Security Standards

### V1 Requirements
* **CSRF Protection:** Implement CSRF protection for all authentication flows
* **Rate Limiting:** Add rate limiting for Discord OAuth attempts and API calls
* **Session Management:** Use secure, httpOnly cookies for session management with proper expiration
* **Input Validation:** All user inputs must be validated using Zod schemas
* **API Security:** Never expose sensitive data in client-side code or logs

### V1.5 Enhancements
* **Error Boundaries:** Implement comprehensive error boundaries for authentication failures
* **Session Security:** Add session timeout and refresh logic for enhanced security
* **Advanced Rate Limiting:** Implement sophisticated rate limiting with Redis

## 5. Performance & Optimization "Secrets"

These are not optional tricks; they are requirements.

### V1 Core Optimizations
1.  **Image Optimization:** All images will be served using the `next/image` component to ensure automatic optimization, modern format conversion (WebP/AVIF), and lazy loading.
2.  **Asset Pre-loading:** For the cinematic onboarding, critical assets (images/videos) must be pre-loaded in the background while the user is on the landing page to ensure an instant, lag-free transition.
3.  **Minimal Client-Side JavaScript:** Use React Server Components (the default in the App Router) wherever possible. Only use the `"use client"` directive for components that truly require interactivity.

### V1.5 Advanced Optimizations
4.  **Lazy Loading Components:** Any large component that is not visible on the initial page load should be loaded dynamically using `next/dynamic`.
5.  **Bundle Size Analysis:** Periodically analyze the application bundle using `@next/bundle-analyzer`.
6.  **Memoization:** Use `React.memo`, `useMemo` and `useCallback` strategically for performance-critical components.

## 6. Performance Monitoring

### V1 Basic Monitoring
* **Vercel Analytics:** Core Web Vitals tracking
* **Basic Error Tracking:** Console error monitoring

### V1.5 Advanced Monitoring
* **Sentry Integration:** Comprehensive error tracking and performance monitoring
* **Custom Metrics:** Implement custom performance metrics for cinematic sequence loading
* **CI/CD Monitoring:** Monitor bundle size in CI/CD pipeline with automated alerts

### V2 Production Monitoring
* **Real-time Monitoring:** Track user interactions and performance bottlenecks
* **Performance Budgets:** Set and enforce performance budgets for key metrics

## 7. Accessibility Standards

### V1 Core Accessibility
* **Motion Sensitivity:** Provide "Skip Cinematic" option for users with motion sensitivity
* **Basic Keyboard Navigation:** Ensure all interactive elements are keyboard accessible
* **Color Contrast:** Ensure color contrast meets WCAG 2.1 AA standards

### V1.5 Enhanced Accessibility
* **ARIA Labels:** Implement comprehensive ARIA labels for all interactive elements
* **Screen Reader Support:** Add comprehensive screen reader support for all UI components
* **Focus Management:** Implement proper focus management for modal dialogs and navigation
* **Alternative Content:** Provide alternative text and descriptions for all visual content

## 8. Development Tooling

### V1 Essential Tools
* **TypeScript:** Strict configuration with no implicit any
* **ESLint + Prettier:** Code quality and formatting
* **Basic Testing:** Jest + React Testing Library for critical paths

### V1.5 Enhanced Tooling
* **Storybook:** Component development and documentation
* **Playwright:** E2E testing of critical user flows
* **Husky:** Pre-commit hooks and automated quality checks

### V2 Production Tooling
* **Chromatic:** Visual regression testing
* **Advanced CI/CD:** Comprehensive testing and deployment pipeline

## 9. Git Workflow

* **Branching Strategy:**
    * `main`: Production branch. Protected. Merges only from `develop`.
    * `develop`: Staging branch. The main integration branch for features.
    * `feature/...`: All new work is done on a feature branch (e.g., `feature/cinematic-onboarding`).
* **Commit Messages:** All commits must follow the **Conventional Commits** specification (e.g., `feat: Add user dashboard layout`, `fix: Correct button alignment on mobile`). This creates a clean, readable history.
* **Phase Tagging:** Use git tags to mark phase completions (v1.0.0, v1.5.0, v2.0.0)

## 10. Cross-Repository Coordination

* **API Contract First:** Always define API contracts before implementing features
* **Synchronized Releases:** Coordinate releases between gategrind-api and gategrind-web
* **Shared Documentation:** Maintain API documentation accessible to both repositories
* **Type Generation:** Automate TypeScript type generation from OpenAPI specs
* **Testing Coordination:** Ensure integration tests cover cross-repository interactions

## 11. Discord Bot Integration Architecture

**CRITICAL**: The web application integrates with an existing, fully-functional Discord bot called "Realm of Shadows" (RoS). Understanding this integration is essential for proper development.

### 11.1 FastAPI Backend Architecture

The `gategrind-api` repository contains both the Discord bot and FastAPI backend:

#### Core Structure
* **Discord Bot**: Built with Pycord, handles Discord interactions and game mechanics
* **FastAPI API**: Provides HTTP endpoints for web application integration
* **Shared Database**: SQLite database shared between Discord bot and web API
* **Unified Models**: Pydantic models used by both Discord bot and FastAPI

#### Key Files & Components
* `api/main.py`: FastAPI application entry point
* `api/models/`: Pydantic models for API contracts
  * `user.py`: UserProfile, UserCreate, UserUpdate models
  * `quest.py`: Quest, QuestCreate, QuestProgress models
  * `auth.py`: DiscordOAuthRequest, TokenResponse models
  * `awakening.py`: AwakeningStatus, ReadinessLevel models
* `api/routes/`: FastAPI route handlers
  * `auth.py`: Discord OAuth2 authentication flow
  * `users.py`: User profile and statistics endpoints
  * `quests.py`: Daily/weekly quest management
  * `awakening.py`: Daily awakening system integration
* `core/api_client.py`: Centralized API client for Discord bot to web integration

### 11.2 Authentication Flow

#### Discord OAuth2 Integration
The web app authenticates users through Discord OAuth2:

1. **Web App → Discord**: Redirect to Discord OAuth2 authorization
2. **Discord → Web App**: Callback with authorization code
3. **Web App → FastAPI**: Exchange code for Discord user data
4. **FastAPI → Web App**: Return JWT token for session management
5. **Web App**: Store JWT in secure httpOnly cookies

#### Key Endpoints
* `POST /api/auth/discord`: Exchange Discord OAuth code for JWT
* `GET /api/auth/me`: Get current authenticated user profile
* `POST /api/auth/refresh`: Refresh expired JWT tokens

### 11.3 Core Game Mechanics Integration

#### The Awakening System
**Central Concept**: Users perform a daily "Awakening" ritual to generate personalized quests.

**Web Integration Points**:
* `GET /api/awakening/status`: Check if user has awakened today
* `POST /api/awakening/awaken`: Perform awakening with readiness level
* `GET /api/awakening/briefing`: Get daily status after awakening

**Readiness Levels**:
* `SHADOW_WHISPER`: Low energy (easier quests)
* `BALANCED_FOCUS`: Standard energy (balanced quests)  
* `PRIMAL_SURGE`: High energy (challenging quests)

#### Quest System
**Daily Quests**: Generated through awakening, tiered by difficulty
* **Tier 1 (Practice)**: Volume-based, rewards Endurance
* **Tier 2 (Technique)**: Form-focused, rewards Technique
* **Tier 3 (Intensity)**: High-intensity, rewards Strength

**Weekly Quests**: Passive tracking + active challenges
* **Vows**: Auto-assigned weekly goals (volume, consistency)
* **Mandates**: Optional high-stakes weekly challenges

**Key Endpoints**:
* `GET /api/quests/daily`: Get current daily quests
* `GET /api/quests/weekly`: Get current weekly quests
* `POST /api/quests/{quest_id}/complete`: Mark quest as completed
* `GET /api/quests/history`: Get quest completion history

#### User Statistics & Progression
**Core Stats**: Strength (STR), Technique (TECH), Endurance (END)
**Progression**: XP-based leveling with stat-specific growth

**Key Endpoints**:
* `GET /api/users/me`: Current user profile with stats
* `GET /api/users/{user_id}`: Public user profile
* `GET /api/users/me/stats/history`: Historical stat progression

### 11.4 Development Mode Support

The FastAPI backend supports both development and production modes:

#### Development Mode Features
* **Mock Data**: Returns realistic mock data when database is unavailable
* **Flexible Authentication**: Supports development without full Discord OAuth setup
* **Graceful Degradation**: API endpoints work even if Discord bot is offline

#### Environment Configuration
```bash
# Development
DEVELOPMENT_MODE=true
MOCK_DATA=true

# Production  
DEVELOPMENT_MODE=false
DATABASE_URL=sqlite:///data/realm_of_shadows.db
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
JWT_SECRET_KEY=your_jwt_secret
```

### 11.5 Data Models & Type Sharing

#### Critical Pydantic Models
```python
# User Profile
class UserProfile(BaseModel):
    user_id: int
    username: str
    display_name: str
    avatar_url: Optional[str]
    level: int
    xp: int
    stats: UserStats  # STR, TECH, END
    
# Quest System
class Quest(BaseModel):
    quest_id: str
    title: str
    description: str
    tier: int  # 1, 2, or 3
    reward_type: str  # "STR", "TECH", "END"
    is_completed: bool
    
# Awakening System
class AwakeningStatus(BaseModel):
    has_awakened_today: bool
    readiness_level: Optional[ReadinessLevel]
    awakening_time: Optional[datetime]
```

#### TypeScript Integration Strategy
1. **OpenAPI Generation**: Auto-generate TypeScript types from FastAPI
2. **Manual Type Definitions**: Create TypeScript interfaces matching Pydantic models
3. **API Client Layer**: Typed functions for all FastAPI endpoints

### 11.6 Integration Requirements

#### V1 Integration Priorities
1. **Discord OAuth Authentication**: Complete login/logout flow
2. **User Dashboard**: Display user stats, level, and current quests
3. **Quest Display**: Show daily quests with completion status
4. **Awakening Interface**: Allow users to perform daily awakening

#### V1.5 Enhanced Integration
1. **Quest History**: Display historical quest completions and streaks
2. **Stat Progression**: Visual charts of stat growth over time
3. **Weekly Quest Tracking**: Display weekly vows and mandate progress

#### V2 Advanced Integration
1. **Real-time Updates**: WebSocket integration for live quest updates
2. **Social Features**: Leaderboards and user comparisons
3. **Advanced Analytics**: Detailed performance metrics and insights

### 11.7 Testing & Development Guidelines

#### Local Development Setup
1. **Run FastAPI Backend**: `uvicorn api.main:app --reload`
2. **Enable Development Mode**: Set `DEVELOPMENT_MODE=true`
3. **Use Mock Data**: Set `MOCK_DATA=true` for frontend development
4. **Test Authentication**: Use development Discord OAuth credentials

#### Integration Testing
* **API Contract Testing**: Ensure web app matches FastAPI endpoint contracts
* **Authentication Flow Testing**: Test complete Discord OAuth flow
* **Data Consistency Testing**: Verify data consistency between Discord bot and web app
* **Error Handling Testing**: Test graceful degradation when backend is unavailable

This integration architecture ensures the web application seamlessly extends the existing Discord bot functionality while maintaining the high-quality, immersive experience that defines the GateGrind ecosystem.