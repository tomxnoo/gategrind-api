import { Client, User } from 'discord.js';
import { Pool } from 'pg';
import { RedisClientType } from 'redis';

export interface ExtendedClient extends Client {
    dbPool: Pool | null;
    redis: RedisClientType | null;
}

export interface UserData {
    user_id: string;
    level: number;
    xp: number;
    total_xp: number;
    daily_quests?: DailyQuests;
    buffs?: Buff[];
    awakening_level?: number;
    [key: string]: any;
}

export interface DailyQuests {
    date: string;
    quests: Quest[];
    rerolled: boolean;
}

export interface Quest {
    id: string;
    title: string;
    description: string;
    movement_type: string;
    target_reps: number;
    current_reps: number;
    xp_reward: number;
    completed: boolean;
}

export interface Buff {
    id: string;
    name: string;
    description: string;
    type: 'active' | 'consumable';
    multiplier?: number;
    duration?: number;
    expires_at?: string;
}

export interface Movement {
    type: string;
    reps: number;
    timestamp: string;
}
