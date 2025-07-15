-- Migration: Add system_settings table for persistent bot configuration
-- Date: 2025-01-17
-- Description: Creates table to store system-wide settings like scheduler state

CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_system_settings_key ON system_settings(setting_key);

-- Insert default incursion scheduler settings
INSERT INTO system_settings (setting_key, setting_value) 
VALUES 
    ('incursion_scheduler_testing_mode', 'true'),
    ('incursion_scheduler_auto_start', 'false')
ON CONFLICT (setting_key) DO NOTHING;