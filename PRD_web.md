# Product Requirements Document: GateGrind Web Application
_Version 3.0 - Final_

## 0. Phased Development Strategy

### V1 (Launch Ready) - Core User Acquisition & Engagement
**Goal:** Convert visitors to active users with a stunning onboarding experience and provide an immediately engaging and useful dashboard.
**Timeline:** 2-3 weeks
**Success Metrics:** Landing page conversion rate > 15%; Day 1 user retention > 30%.

### V1.5 (First Major Update) - Richer Experience & Community Focus
**Goal:** Enhance user retention with more detailed progress tracking and community features.
**Timeline:** 4-6 weeks post-V1
**Success Metrics:** User dashboard engagement > 60%; 7-day user retention > 40%.

### V2 (Production-Grade) - Real-time & Advanced Features
**Goal:** Deliver a premium, real-time experience that solidifies GateGrind as a leader in fitness gamification.
**Timeline:** 8-12 weeks post-V1.5
**Success Metrics:** High feature adoption; excellent performance metrics; positive community feedback.

## 1. Overview & Vision
GateGrind is a gamified fitness RPG bot for Discord. The `gategrind.com` website serves as the primary entry point and user dashboard for the ecosystem, providing an immersive experience for its users, known as **Ascendants**.

The website's primary goal is to **convert visitors into active users** by providing an immersive and intriguing first impression that seamlessly leads to Discord authentication. The secondary goal is to provide a rich, performant dashboard for existing users to track their progress and daily objectives.

## 2. Target Audience
* **Primary:** Tech-savvy fitness enthusiasts, gamers, and RPG fans who are active on Discord.
* **Secondary:** Discord community owners looking for novel ways to engage their members.

## 3. User Flows

### Flow 1: New User Onboarding ("The Cinematic")
1. **Arrival:** User lands on `gategrind.com`. They see a minimalist page with an animated "Empty Portal" background and a single "Connect to the System" CTA.
2. **Initiation:** User clicks the CTA. The UI fades out.
3. **The Sequence Begins:** A full-screen, pre-rendered video sequence plays (The "Walk" Phase implementation).
   * **Scene A:** A first-person view of a hand reaching for the portal. A glowing 'GG' tattoo appears on the forearm.
   * **Scene B:** A third-person view of the "Primal Warrior" archetype walking towards and through the portal.
   * **Scene C:** A brief, abstract "vortex/swirl" effect.
4. **Completion:** The sequence ends.
5. **Arrival at Dashboard:** The user is seamlessly transitioned to their newly created User Dashboard.

### Flow 2: Returning User Login
1. **Arrival:** User lands on `gategrind.com`.
2. **Initiation:** User clicks "Connect to the System."
3. **Authentication:** The Discord OAuth flow completes. Since the user is already registered, they bypass the cinematic sequence.
4. **Arrival at Dashboard:** The user is immediately taken to their User Dashboard.

## 4. Feature Requirements

### FR-1: Public-Facing Pages

#### V1 Requirements
* **1.1 Landing Page (`/`):**
  * Must feature a full-screen, looping, performant animated background video (`.webm`).
  * Must have a single, prominent, centered CTA button: "Connect to the System."
  * Must include a clean navigation header.
  * Must provide fallback static images for slow connections or devices that struggle with video playback.
  * Must include accessible "Skip Cinematic" option for users with motion sensitivity.
* **1.2 Navigation Header:**
  * Must contain links to: Features (`/features`), FAQ (`/faq`), and a CTA to join the Discord (`/discord`).

#### V1.5 Enhancements
* **1.3 Features Page (`/features`):**
  * A static marketing page showcasing the bot's core mechanics (Stats, Quests, Incursions).
  * Must feature the brand's "Hero Imagery" (e.g., the Primal Warrior).
* **1.4 FAQ Page (`/faq`):**
  * A static page with answers to common questions.

### FR-2: User Authentication

#### V1 Requirements
* **2.1:** Authentication must be handled exclusively through Discord OAuth2 using NextAuth.js with the Discord Provider.
* **2.2:** The system must differentiate between new and returning users to direct them to the correct user flow (Cinematic vs. Direct to Dashboard).
* **2.3:** Basic error handling for authentication failures with user-friendly messages.

#### V1.5 Enhancements
* **2.4:** Comprehensive error handling including rate limiting and retry logic.
* **2.5:** Handle Discord OAuth edge cases (denied permissions, network failures, etc.).
* **2.6:** Advanced session management with timeout and refresh logic.

### FR-3: User Dashboard (`/dashboard`)

#### V1 Core Dashboard - The Command Center
*This initial dashboard must be immediately useful and engaging to encourage retention.*
* **3.1 Welcome Widget:** Displays a personalized greeting: `"Continue your Ascension, Ascendant [Username]"`.
* **3.2 Core Stats Widget:** Displays the user's current `STR`, `END`, and `TECH` stats, fetched from the FastAPI backend.
* **3.3 Awakening Status Widget:** A prominent widget displaying the user's daily ritual status.
  * Must show if the user has completed their daily Awakening (e.g., "Status: High Awakening Protocol").
  * If not yet awakened, it must feature a strong CTA that directs the user to perform the Awakening ritual in Discord.
* **3.4 Quest & Contract Terminal:** A unified widget to display objectives with clear sections or tabs for "Daily Quests" (from the Awakening system) and "Weekly Contracts."
  * Essential for completing the core gameplay loop: Awaken → Get Quests → Log Workout
* **3.5 "Log Workout" CTA:** A prominent button or link that directs the user to the Discord bot to log a new workout.
* **3.6 Logout Functionality:** A user must be able to log out, destroying their session.

#### V1.5 Enhanced Dashboard
* **3.7 Recent Activity Widget:** Displays a list of the user's last 5-7 logged workouts.
* **3.8 Shadow Incursion Status:** A widget that displays information about active world events.
  * If an incursion is active, it must show the objective, time remaining, and a community progress bar.
  * If no incursion is active, it should display a "System is Clear" or similar status.
* **3.9 Stat Progression Charts:** Visual charts showing the user's stat growth over time.

#### V2 Advanced Dashboard
* **3.10 Data Loading Strategy:**
  * Implement React Query/TanStack Query for caching and background updates
  * Use Suspense boundaries for progressive loading of dashboard widgets
  * Implement optimistic updates for user actions
  * Add offline-first capabilities with service workers for core functionality
* **3.11 Real-time Features:**
  * WebSocket connection for live quest updates and progress tracking
  * Real-time Shadow Incursion progress updates
  * Push notifications for quest completions and important events

### FR-4: Performance & Accessibility Requirements

#### V1 Core Requirements
* **4.1 Performance:**
  * Initial page load must be under 3 seconds on 3G connections
  * Core Web Vitals must meet "Needs Improvement" thresholds minimum
  * Video preloading strategy with loading states for cinematic sequence
  * Basic video format support (WebM with MP4 fallback)
* **4.2 Accessibility:**
  * Provide "Skip Cinematic" option for users with motion sensitivity
  * Basic keyboard navigation for all interactive elements
  * Ensure color contrast meets WCAG 2.1 AA standards

#### V1.5 Enhanced Requirements
* **4.3 Performance:**
  * Initial page load under 2 seconds on 3G connections
  * Core Web Vitals must meet "Good" thresholds
  * Advanced video optimization with multiple format support
* **4.4 Accessibility:**
  * Implement comprehensive ARIA labels and keyboard navigation
  * Add screen reader support for all interactive elements
  * Focus management for modal dialogs and navigation

### FR-5: Error Handling & Edge Cases

#### V1 Basic Error Handling
* **5.1:** Basic error boundaries for authentication and critical components
* **5.2:** Simple retry logic for failed API calls
* **5.3:** User-friendly error messages with basic next steps

#### V1.5 Comprehensive Error Handling
* **5.4:** Comprehensive error boundaries for all major components
* **5.5:** Graceful degradation when API services are unavailable
* **5.6:** Advanced retry logic with exponential backoff
* **5.7:** Offline mode support for viewing cached dashboard data

## 5. Technical Architecture Requirements

### TA-1: API Client Layer

#### V1 Basic Client
* Must implement a basic API client for authentication and core dashboard data
* Basic TypeScript types for API responses
* Simple error handling and authentication token management

#### V1.5 Enhanced Client
* Comprehensive API client that mirrors the FastAPI backend structure
* Advanced TypeScript types generated from OpenAPI specs
* Sophisticated request/response interceptors and error handling

### TA-2: State Management

#### V1 Basic State
* Basic Zustand store for user session and authentication state
* Simple React Query setup for server state caching

#### V1.5 Advanced State
* Comprehensive global state management using Zustand
* Advanced React Query configuration with background updates and caching strategies
* Form state management using React Hook Form with Zod validation

### TA-3: Component Architecture

#### V1 Basic Components
* Basic component structure following atomic design principles
* Essential TypeScript interfaces for component props
* Simple component composition for core features

#### V1.5 Advanced Components
* Comprehensive atomic design implementation with clear component hierarchy
* Advanced component composition and reusability patterns
* Full TypeScript interfaces for all component props and data structures

## 6. Discord Bot Integration Requirements

### DBI-1: FastAPI Backend Integration
The web application must integrate with the existing FastAPI backend that powers the Discord bot.

#### Current Architecture
* **FastAPI Backend** (`api/`): RESTful API server handling all business logic
* **Discord Bot Client** (`main.py` + `features/`): UI layer making API calls to FastAPI
* **Shared Core** (`core/`): Database, Redis cache, and API client utilities
* **Database**: PostgreSQL with AsyncPG connection pooling

#### Key API Endpoints for Web Integration
/api/auth/
├── /discord/callback     # Discord OAuth2 callback
├── /login               # JWT token generation
└── /refresh             # Token refresh

/api/users/
├── /me                  # Current user profile
└── /{user_id}          # Public user profile

/api/awakening/
├── /status              # Daily awakening status
├── /awaken              # Perform awakening ritual
└── /quests              # Get today's quests

/api/quests/
├── /daily               # Daily quest management
├── /weekly              # Weekly quest management
└── /history             # Quest completion history

/api/logging/
├── /reps                # Log workout reps
└── /history             # Workout history

/api/incursions/
├── /active              # Active Shadow Incursions
└── /history             # Incursion history

/api/buffs/
├── /active              # Active user buffs
└── /available           # Available buffs


#### Authentication Flow
1. **Discord OAuth2**: User authenticates 
via Discord
2. **JWT Generation**: Backend creates 
JWT token with user claims
3. **Session Management**: Web app stores 
JWT in httpOnly cookies
4. **API Requests**: All API calls 
include JWT for authentication

#### Data Models (TypeScript Types Needed)

// User Models
interface UserProfile {
  user_id: number;
  discord_id: string;
  username: string;
  level: number;
  xp: number;
  xp_max: number;
  stats: {
    STR: StatData;
    END: StatData;
    TECH: StatData;
  };
  active_buffs: Record<string, BuffData>;
  created_at: string;
  updated_at: string;
}

interface StatData {
  level: number;
  xp: number;
  xp_max: number;
}

// Quest Models
interface Quest {
  id: number;
  title: string;
  description: string;
  tier: 1 | 2 | 3; // Practice, 
  Technique, Intensity
  xp_reward: number;
  status: 'available' | 'active' | 
  'completed' | 'expired';
  progress: QuestProgress;
  expires_at?: string;
}

// Awakening Models
interface AwakeningStatus {
  awakened: boolean;
  readiness_level?: 'shadow' | 
  'warrior' | 'ascendant';
  quest_count: number;
  quests: Quest[];
}


### DBI-2: Core Game Mechanics Integration

#### The Awakening System
The web dashboard must integrate with the 
core "Awakening" ritual:
1. **Status Check**: Display if user has 
awakened today
2. **Readiness Selection**: Allow users 
to choose energy level (Shadow/Warrior/
Ascendant)
3. **Quest Generation**: Show generated 
quests based on readiness level
4. **Progress Tracking**: Display quest 
completion status

#### Quest System Integration
* **Daily Quests**: Generated through 
Awakening ritual
* **Weekly Contracts**: Long-term 
objectives
* **Quest Tiers**: 
  - Tier 1 (Practice): Volume-based, 
  rewards END
  - Tier 2 (Technique): Form-focused, 
  rewards TECH  
  - Tier 3 (Intensity): High-intensity, 
  rewards STR

#### Shadow Incursions (Dynamic Events)
* **Active Events**: Display current 
world events
* **Community Progress**: Show 
server-wide participation
* **Time-Limited**: Events have 
expiration timers

### DBI-3: Development Mode Support
The FastAPI backend includes development 
mode for testing:
* **Mock Data**: Returns sample data when 
`DEV_MODE=true`
* **No Database Required**: Can run 
without PostgreSQL connection
* **Authentication Bypass**: Simplified 
auth for development

### DBI-4: Environment Configuration
Required environment variables for web 
app:


# API Configuration
API_BASE_URL=http://localhost:8000/api
JWT_SECRET_KEY=your-jwt-secret

# Discord OAuth
DISCORD_CLIENT_ID=your-discord-client-id
DISCORD_CLIENT_SECRET=your-discord-client-
secret
DISCORD_REDIRECT_URI=http://
localhost:3000/api/auth/callback

# Development
DEV_MODE=false
NODE_ENV=development


## 8. Monitoring & Analytics Requirements

### MA-1: Performance Monitoring

#### V1 Basic Monitoring
* Basic Vercel Analytics for Core Web 
Vitals tracking
* Console-based error logging

#### V1.5 Advanced Monitoring
* Comprehensive error tracking with 
Sentry integration
* Custom performance metrics for 
cinematic sequence loading
* Bundle size monitoring in CI/CD pipeline

#### V2 Production Monitoring
* Real-time performance monitoring and 
alerting
* Advanced analytics with user behavior 
tracking
* Performance budgets with automated 
enforcement

### MA-2: User Analytics

#### V1 Basic Analytics
* Basic conversion tracking from landing 
page to Discord authentication
* Simple user engagement metrics

#### V1.5 Enhanced Analytics
* Detailed user engagement tracking with 
cinematic sequence
* Dashboard widget usage and interaction 
patterns
* User retention and feature adoption 
analysis

#### V2 Advanced Analytics
* Comprehensive user journey analysis
* A/B testing framework for feature 
optimization
* Advanced retention and engagement 
metrics