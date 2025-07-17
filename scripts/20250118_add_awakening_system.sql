-- Migration: Add awakening system tables
-- Date: 2025-01-18
-- Description: Creates tables for the daily awakening ritual and quest generation system

-- Create awakening_sessions table to track daily awakenings
CREATE TABLE IF NOT EXISTS awakening_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    awakening_date DATE NOT NULL,
    readiness_level VARCHAR(20) NOT NULL CHECK (readiness_level IN ('low', 'standard', 'high')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'awakened', 'completed')),
    quest_count INTEGER NOT NULL DEFAULT 3 CHECK (quest_count >= 1 AND quest_count <= 5),
    generated_quests INTEGER[] DEFAULT '{}',  -- Array of quest IDs
    completed_quests INTEGER[] DEFAULT '{}',  -- Array of completed quest IDs
    total_xp_gained INTEGER DEFAULT 0,
    awakened_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure one awakening per user per day
    UNIQUE(user_id, awakening_date)
);

-- Create awakening_quests table for quest details
CREATE TABLE IF NOT EXISTS awakening_quests (
    id SERIAL PRIMARY KEY,
    awakening_session_id INTEGER NOT NULL REFERENCES awakening_sessions(id) ON DELETE CASCADE,
    quest_data JSONB NOT NULL,  -- Complete quest definition
    tier INTEGER NOT NULL CHECK (tier IN (1, 2, 3)),  -- Practice/Technique/Intensity
    xp_reward INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'active', 'completed', 'expired', 'abandoned')),
    progress JSONB DEFAULT '{}',  -- Quest progress tracking
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create readiness_history table to track readiness patterns
CREATE TABLE IF NOT EXISTS readiness_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    readiness_level VARCHAR(20) NOT NULL CHECK (readiness_level IN ('low', 'standard', 'high')),
    factors JSONB DEFAULT '{}',  -- Factors influencing readiness (sleep, stress, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure one readiness entry per user per day
    UNIQUE(user_id, date)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_awakening_sessions_user_date ON awakening_sessions(user_id, awakening_date);
CREATE INDEX IF NOT EXISTS idx_awakening_sessions_status ON awakening_sessions(status);
CREATE INDEX IF NOT EXISTS idx_awakening_quests_session ON awakening_quests(awakening_session_id);
CREATE INDEX IF NOT EXISTS idx_awakening_quests_status ON awakening_quests(status);
CREATE INDEX IF NOT EXISTS idx_readiness_history_user_date ON readiness_history(user_id, date);

-- Add awakening-related fields to user_json_data for caching
-- This will store awakening preferences and autoregulation data
-- Example structure:
-- {
--   "awakening_preferences": {
--     "preferred_quest_count": 3,
--     "autoregulation_enabled": true,
--     "readiness_factors": ["sleep", "stress", "energy"]
--   },
--   "awakening_stats": {
--     "total_awakenings": 0,
--     "completion_streak": 0,
--     "average_readiness": "standard",
--     "preferred_readiness": "standard"
--   }
-- }