-- Migration: Add active_incursions table for Shadow Incursions feature
-- Date: 2025-01-15
-- Description: Creates the core table to track live incursion events

CREATE TABLE IF NOT EXISTS active_incursions (
    id SERIAL PRIMARY KEY,
    incursion_id VARCHAR(50) UNIQUE NOT NULL,
    incursion_type VARCHAR(20) NOT NULL CHECK (incursion_type IN ('surge', 'challenge', 'anomaly')),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    target_exercise VARCHAR(50) NOT NULL,
    target_reps INTEGER NOT NULL,
    current_reps INTEGER DEFAULT 0,
    reward_type VARCHAR(20) NOT NULL CHECK (reward_type IN ('xp', 'buff', 'item')),
    reward_value INTEGER NOT NULL,
    reward_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_active_incursions_active ON active_incursions(is_active);
CREATE INDEX IF NOT EXISTS idx_active_incursions_expires ON active_incursions(expires_at);
CREATE INDEX IF NOT EXISTS idx_active_incursions_type ON active_incursions(incursion_type);
CREATE INDEX IF NOT EXISTS idx_active_incursions_exercise ON active_incursions(target_exercise);

-- Add comments for documentation
COMMENT ON TABLE active_incursions IS 'Tracks live Shadow Incursion events with community progress';
COMMENT ON COLUMN active_incursions.incursion_id IS 'Unique identifier for the incursion (e.g., SURGE_001, CHALLENGE_042)';
COMMENT ON COLUMN active_incursions.metadata IS 'Additional incursion data (difficulty modifiers, special conditions, etc.)';