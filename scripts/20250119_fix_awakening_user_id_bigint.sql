-- Migration: Fix user_id data type in awakening system tables
-- Date: 2025-01-19
-- Description: Changes user_id columns from INTEGER to BIGINT to support Discord user IDs

-- Discord user IDs are 64-bit integers, so they need BIGINT instead of INTEGER

-- Fix awakening_sessions table
ALTER TABLE awakening_sessions 
ALTER COLUMN user_id TYPE BIGINT;

-- Fix readiness_history table  
ALTER TABLE readiness_history
ALTER COLUMN user_id TYPE BIGINT;

-- Note: awakening_quests table doesn't have a direct user_id column,
-- it references awakening_sessions through awakening_session_id which is fine

-- The foreign key constraints should be automatically updated by PostgreSQL
-- but let's verify the users table also uses BIGINT for user_id

-- If the users table doesn't exist or uses INTEGER, we need to fix it too
-- This is a safe operation that will only run if the table exists
DO $$
BEGIN
    -- Check if users table exists and has INTEGER user_id
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'user_id' 
        AND data_type = 'integer'
    ) THEN
        -- Update users table to use BIGINT
        ALTER TABLE users ALTER COLUMN user_id TYPE BIGINT;
        RAISE NOTICE 'Updated users.user_id to BIGINT';
    END IF;
    
    -- Check and update user_stats table if needed
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_stats' 
        AND column_name = 'user_id' 
        AND data_type = 'integer'
    ) THEN
        ALTER TABLE user_stats ALTER COLUMN user_id TYPE BIGINT;
        RAISE NOTICE 'Updated user_stats.user_id to BIGINT';
    END IF;
    
    -- Check and update user_json_data table if needed
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_json_data' 
        AND column_name = 'user_id' 
        AND data_type = 'integer'
    ) THEN
        ALTER TABLE user_json_data ALTER COLUMN user_id TYPE BIGINT;
        RAISE NOTICE 'Updated user_json_data.user_id to BIGINT';
    END IF;
    
    -- Check and update health_data table if needed
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'health_data' 
        AND column_name = 'user_id' 
        AND data_type = 'integer'
    ) THEN
        ALTER TABLE health_data ALTER COLUMN user_id TYPE BIGINT;
        RAISE NOTICE 'Updated health_data.user_id to BIGINT';
    END IF;
    
    -- Check and update any other tables that might have user_id as INTEGER
    -- Add more tables as needed...
    
END $$;