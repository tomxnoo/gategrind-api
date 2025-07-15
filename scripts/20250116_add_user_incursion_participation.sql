-- Migration: Add user_incursion_participation table for Shadow Incursions feature
-- Date: 2025-01-16
-- Description: Creates the table to track user participation in incursions

CREATE TABLE IF NOT EXISTS user_incursion_participation (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    incursion_id VARCHAR(50) NOT NULL,
    reps_contributed INTEGER NOT NULL DEFAULT 0,
    participated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_notes TEXT,
    FOREIGN KEY (incursion_id) REFERENCES active_incursions(incursion_id) ON DELETE CASCADE
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_user_incursion_participation_user ON user_incursion_participation(user_id);
CREATE INDEX IF NOT EXISTS idx_user_incursion_participation_incursion ON user_incursion_participation(incursion_id);
CREATE INDEX IF NOT EXISTS idx_user_incursion_participation_user_incursion ON user_incursion_participation(user_id, incursion_id);
CREATE INDEX IF NOT EXISTS idx_user_incursion_participation_participated_at ON user_incursion_participation(participated_at);

-- Add comments for documentation
COMMENT ON TABLE user_incursion_participation IS 'Tracks individual user participation and contributions to Shadow Incursions';
COMMENT ON COLUMN user_incursion_participation.user_id IS 'Discord user ID of the participant';
COMMENT ON COLUMN user_incursion_participation.incursion_id IS 'Reference to the incursion being participated in';
COMMENT ON COLUMN user_incursion_participation.reps_contributed IS 'Number of reps contributed in this participation session';
COMMENT ON COLUMN user_incursion_participation.session_notes IS 'Optional notes about the participation session';