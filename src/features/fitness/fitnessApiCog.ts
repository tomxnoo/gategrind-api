import axios from 'axios';
import { RealmBot } from '../../main';

/**
 * Fitness API Cog
 * Handles external fitness API integration (Garmin, etc.)
 */
export class FitnessApiCog {
    private bot: RealmBot;
    private fitnessHubUrl: string;

    constructor(bot: RealmBot) {
        this.bot = bot;
        this.fitnessHubUrl = 'https://syncros.replit.app';
    }

    /**
     * Sync fitness data from external API
     */
    async syncFitnessData(userId: string, forceRefresh: boolean = false, syncDate?: string): Promise<any> {
        try {
            const date = syncDate || new Date().toISOString().split('T')[0];
            const endpoint = `${this.fitnessHubUrl}/api/sync/${userId}?date=${date}&refresh=${forceRefresh}`;

            const response = await axios.get(endpoint);
            console.log(`[DEBUG] Fitness sync response for user ${userId}:`, response.data);

            return response.data;
        } catch (error) {
            console.error('[FITNESS_API] Error syncing fitness data:', error);
            throw error;
        }
    }

    registerHandlers(): void {
        // API handlers would go here
    }
}

export async function setup(bot: RealmBot): Promise<void> {
    const cog = new FitnessApiCog(bot);
    cog.registerHandlers();
    console.log('[OK] Fitness API cog loaded');
}
