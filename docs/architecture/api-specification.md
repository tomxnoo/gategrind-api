# API Specification

## Overview

The GateGrind V2 API follows RESTful principles and is versioned under the `/v2/` namespace. All endpoints are organized into logical routers for clarity and maintainability. The API is built with FastAPI, providing automatic documentation and validation.

## API Design Principles

### 1. RESTful Design
- Standard HTTP methods (GET, POST, PUT, DELETE)
- Resource-based URLs
- Consistent response formats
- Proper HTTP status codes

### 2. Versioning Strategy
- All V2 endpoints prefixed with `/v2/`
- Backward compatibility maintained where possible
- Clear deprecation path for V1 endpoints

### 3. Response Consistency
- Standardized response format across all endpoints
- Consistent error handling and messaging
- Real-time Aura updates in progression responses

### 4. Performance Optimization
- Asynchronous operations for long-running tasks
- Comprehensive caching strategy
- Optimized data transfer with DTOs

## Core Endpoints

### User Profile Management

#### GET /v2/users/me/profile
**Purpose**: Returns comprehensive Profile Panel DTO for Discord UI rendering.

**Response Format**:
```json
{
  "ascendant": {
    "id": 12345,
    "discord_id": "123456789012345678",
    "username": "FitnessWarrior",
    "level": 25,
    "global_xp": 15000,
    "aura": 1250,
    "last_login": "2024-01-15T10:30:00Z"
  },
  "stats": {
    "strength": {
      "level": 8,
      "xp": 1200,
      "points": 3,
      "next_milestone": 1500
    },
    "endurance": {
      "level": 6,
      "xp": 800,
      "points": 2,
      "next_milestone": 1000
    },
    "technique": {
      "level": 10,
      "xp": 2000,
      "points": 5,
      "next_milestone": 2500
    }
  },
  "progression": {
    "unlocked_skills": [
      {
        "node_id": 1,
        "name": "Basic Pushup",
        "category": "PUSH_VERTICAL",
        "unlocked_at": "2024-01-10T14:20:00Z"
      }
    ],
    "available_points": {
      "strength": 3,
      "endurance": 2,
      "technique": 5
    },
    "next_milestone": {
      "type": "level",
      "target": 30,
      "progress": 15000,
      "required": 18000
    }
  },
  "daily_status": {
    "awakening_completed": false,
    "login_reward_claimed": true,
    "shadow_keys": 3,
    "active_quests": 2
  }
}
```

**Caching**: 5-minute Redis cache, invalidated on profile changes.

### Movement & Skill Tree

#### GET /v2/movements/library
**Purpose**: Returns the complete skill tree library structure.

**Response Format**:
```json
{
  "categories": [
    {
      "id": "PUSH_VERTICAL",
      "name": "Vertical Push",
      "description": "Overhead and vertical pushing movements",
      "skill_nodes": [
        {
          "id": 1,
          "level": 1,
          "name": "Basic Pushup",
          "description": "Foundation pushing movement",
          "requirements": {
            "ascendant_level": 1,
            "strength_points": 0,
            "endurance_points": 0,
            "technique_points": 0
          },
          "movements": [
            {
              "id": 1,
              "name": "Standard Pushup",
              "xp_per_rep": 1
            }
          ]
        }
      ]
    }
  ]
}
```

**Caching**: Heavily cached in Redis (1-hour TTL), as this data changes rarely.

### Progression System

#### POST /v2/progression/unlock-skill
**Purpose**: Unlocks a skill node for the user.

**Request Body**:
```json
{
  "node_id": 5,
  "confirm_point_expenditure": true
}
```

**Response Format**:
```json
{
  "success": true,
  "data": {
    "unlocked_node": {
      "id": 5,
      "name": "Diamond Pushup",
      "category": "PUSH_VERTICAL"
    },
    "points_consumed": {
      "strength": 2,
      "technique": 1
    },
    "remaining_points": {
      "strength": 1,
      "endurance": 2,
      "technique": 4
    }
  },
  "aura_update": {
    "previous_aura": 1200,
    "new_aura": 1250,
    "change": 50,
    "reason": "Skill unlock: Diamond Pushup"
  }
}
```

#### POST /v2/events/log-movement
**Purpose**: Re-implemented movement logging endpoint.

**Request Body**:
```json
{
  "movement_id": 1,
  "reps": 20,
  "session_id": "optional_session_tracking"
}
```

**Response Format**:
```json
{
  "success": true,
  "data": {
    "movement": {
      "id": 1,
      "name": "Standard Pushup"
    },
    "reps_logged": 20,
    "xp_earned": {
      "global": 20,
      "strength": 15,
      "endurance": 10
    },
    "level_ups": [
      {
        "type": "strength",
        "new_level": 9,
        "points_earned": 1
      }
    ]
  },
  "aura_update": {
    "previous_aura": 1250,
    "new_aura": 1275,
    "change": 25,
    "reason": "Strength level up"
  }
}
```

### Awakening System

#### POST /v2/awakening/generate
**Purpose**: Initiates daily Awakening ritual.

**Response Format**:
```json
{
  "success": true,
  "data": {
    "awakening_id": "awk_20240115_12345",
    "shadow_key_awarded": true,
    "quests_generated": [
      {
        "id": 101,
        "title": "Morning Strength",
        "description": "Complete 50 pushups to start your day strong",
        "target_movement": "Standard Pushup",
        "target_reps": 50,
        "reward_xp": 100,
        "expires_at": "2024-01-16T00:00:00Z"
      }
    ],
    "daily_modifier": {
      "type": "strength_focus",
      "description": "Strength exercises provide 25% bonus XP today"
    }
  }
}
```

### Dungeon System

#### POST /v2/dungeons/enter
**Purpose**: Enters a dungeon level (asynchronous operation).

**Request Body**:
```json
{
  "dungeon_level": 3,
  "shadow_keys_to_spend": 1
}
```

**Immediate Response (202 Accepted)**:
```json
{
  "task_id": "dungeon_entry_abc123",
  "status": "processing",
  "estimated_completion": "30s",
  "message": "Generating your dungeon trial..."
}
```

**Task Status Check (GET /v2/tasks/{task_id}/status)**:
```json
{
  "task_id": "dungeon_entry_abc123",
  "status": "completed",
  "result": {
    "dungeon_entry": {
      "level": 3,
      "trial_quest": {
        "id": 201,
        "title": "Trial of Endurance",
        "description": "Prove your endurance in the shadow realm",
        "requirements": [
          {
            "movement": "Burpees",
            "target_reps": 100,
            "time_limit": "10 minutes"
          }
        ],
        "rewards": {
          "xp": 500,
          "shadow_keys": 2,
          "special_items": ["Endurance Boost"]
        }
      }
    }
  }
}
```

### Daily Login System

#### POST /v2/events/login
**Purpose**: Processes daily login and distributes rewards.

**Response Format**:
```json
{
  "success": true,
  "data": {
    "login_streak": 7,
    "total_logins": 45,
    "reward": {
      "type": "streak_bonus",
      "tier": "week_complete",
      "items": [
        {
          "type": "xp",
          "amount": 500
        },
        {
          "type": "shadow_keys",
          "amount": 3
        },
        {
          "type": "stat_points",
          "strength": 1,
          "endurance": 1
        }
      ]
    },
    "next_reward_preview": {
      "days_until": 1,
      "reward_type": "daily_bonus",
      "estimated_value": "150 XP"
    }
  }
}
```

## Utility Endpoints

### Health Check

#### GET /health
**Purpose**: Service health verification.

**Response Format**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "2.0.0",
  "dependencies": {
    "database": "connected",
    "redis": "connected",
    "sentry": "active"
  }
}
```

### Task Management

#### GET /v2/tasks/{task_id}/status
**Purpose**: Check status of asynchronous operations.

**Response Format**:
```json
{
  "task_id": "abc123",
  "status": "completed|processing|failed",
  "progress": 100,
  "result": {
    // Task-specific result data
  },
  "error": null,
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:30Z"
}
```

## Error Handling

### Standard Error Response
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_POINTS",
    "message": "Not enough stat points to unlock this skill",
    "details": {
      "required": {
        "strength": 3,
        "technique": 2
      },
      "available": {
        "strength": 1,
        "technique": 2
      }
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Status Codes
- **200 OK**: Successful operation
- **201 Created**: Resource created successfully
- **202 Accepted**: Asynchronous operation initiated
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Business rule violation
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

## Authentication & Authorization

### Discord OAuth Integration
- JWT tokens for API authentication
- Discord user ID mapping to internal user IDs
- Role-based access control for admin endpoints

### Rate Limiting
- Per-user rate limits to prevent abuse
- Different limits for different endpoint categories
- Graceful degradation under high load

## API Documentation

### Automatic Documentation
- OpenAPI/Swagger documentation auto-generated by FastAPI
- Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)
- Comprehensive request/response examples

### Versioning Strategy
- V2 endpoints maintain backward compatibility where possible
- Clear migration path from V1 to V2
- Deprecation notices for outdated endpoints

---
*This API specification provides a comprehensive, performant, and user-friendly interface for all GateGrind V2 functionality while maintaining consistency and reliability.*