import { Pool, PoolClient } from 'pg';
import { RealmBot } from '../main';

/**
 * Database manager for user data operations
 */
export class DataManager {
    private bot: RealmBot;

    constructor(bot: RealmBot) {
        this.bot = bot;
    }

    /**
     * Get user profile from database
     */
    async getUserProfile(userId: string): Promise<any> {
        if (!this.bot.dbPool) {
            throw new Error('Database pool not initialized');
        }

        const client = await this.bot.dbPool.connect();
        try {
            const result = await client.query(
                'SELECT * FROM user_profiles WHERE user_id = $1',
                [userId]
            );
            
            if (result.rows.length === 0) {
                // Create default profile
                return await this.createUserProfile(userId, client);
            }

            return result.rows[0];
        } finally {
            client.release();
        }
    }

    /**
     * Create default user profile
     */
    private async createUserProfile(userId: string, client: PoolClient): Promise<any> {
        const defaultProfile = {
            user_id: userId,
            level: 1,
            xp: 0,
            total_xp: 0,
            created_at: new Date(),
        };

        await client.query(
            `INSERT INTO user_profiles (user_id, level, xp, total_xp, created_at)
             VALUES ($1, $2, $3, $4, $5)
             ON CONFLICT (user_id) DO NOTHING`,
            [userId, defaultProfile.level, defaultProfile.xp, defaultProfile.total_xp, defaultProfile.created_at]
        );

        return defaultProfile;
    }

    /**
     * Update user XP
     */
    async updateUserXp(userId: string, xpToAdd: number): Promise<any> {
        if (!this.bot.dbPool) {
            throw new Error('Database pool not initialized');
        }

        const client = await this.bot.dbPool.connect();
        try {
            const result = await client.query(
                `UPDATE user_profiles 
                 SET xp = xp + $2, total_xp = total_xp + $2
                 WHERE user_id = $1
                 RETURNING *`,
                [userId, xpToAdd]
            );

            return result.rows[0];
        } finally {
            client.release();
        }
    }

    /**
     * Get daily quests for user
     */
    async getDailyQuests(userId: string): Promise<any[]> {
        if (!this.bot.dbPool) {
            throw new Error('Database pool not initialized');
        }

        const client = await this.bot.dbPool.connect();
        try {
            const result = await client.query(
                `SELECT * FROM daily_quests 
                 WHERE user_id = $1 
                 AND date = CURRENT_DATE
                 ORDER BY created_at`,
                [userId]
            );

            return result.rows;
        } finally {
            client.release();
        }
    }
}
