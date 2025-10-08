import * as Sentry from '@sentry/node';
import { config } from 'dotenv';
import { Client, GatewayIntentBits, ActivityType, Partials } from 'discord.js';
import * as path from 'path';
import { Pool } from 'pg';
import { createClient, RedisClientType } from 'redis';
import { startFastifyServer } from './api/server';

// Initialize Sentry
Sentry.init({
    dsn: "https://a79a94e31ba80fa8835018abc3e28dfb@o4509645249118208.ingest.de.sentry.io/4509645253312592",
    tracesSampleRate: 1.0,
});

// Load environment variables
config();

const TOKEN = process.env.DISCORD_TOKEN;
const DATABASE_URL = process.env.DATABASE_URL;
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379/0';

// Extended client to hold database and redis connections
export class RealmBot extends Client {
    public dbPool: Pool | null = null;
    public redis: RedisClientType | null = null;

    constructor() {
        super({
            intents: [
                GatewayIntentBits.Guilds,
                GatewayIntentBits.GuildMessages,
                GatewayIntentBits.MessageContent,
            ],
            partials: [Partials.Channel],
            shards: 'auto', // Auto-sharding equivalent to AutoShardedBot
        });
    }

    async setupDatabase(): Promise<void> {
        console.log('[INFO] Initializing database connection pool...');
        try {
            this.dbPool = new Pool({
                connectionString: DATABASE_URL,
                min: 5,
                max: 20,
                connectionTimeoutMillis: 60000,
            });
            
            // Test connection
            const client = await this.dbPool.connect();
            client.release();
            console.log('[OK] Database connection pool created successfully.');
        } catch (error) {
            console.error('[FAIL] Could not create database connection pool:', error);
            throw error;
        }
    }

    async setupRedis(): Promise<void> {
        console.log('[INFO] Connecting to Redis...');
        try {
            this.redis = createClient({ url: REDIS_URL });
            
            this.redis.on('error', (err) => {
                console.error('[ERROR] Redis client error:', err);
            });

            await this.redis.connect();
            console.log('[OK] Connected to Redis successfully.');
        } catch (error) {
            console.error('[FAIL] Could not connect to Redis:', error);
            throw error;
        }
    }

    async loadExtensions(): Promise<void> {
        console.log('[INFO] Loading Discord bot extensions...');
        
        const extensions = [
            'system/systemHubCog',
            'awakening/awakeningCog',
            'buffs/buffsCog',
            'logging/loggingCog',
            'quests/questsCog',
            'user/userCog',
            'moderation/messageManagementCog',
            'moderation/rerollResetCog',
            'moderation/questCompletionCog',
            'fitness/fitnessSyncCog',
            'fitness/fitnessApiCog',
            'incursions/incursionsCog',
        ];

        for (const ext of extensions) {
            try {
                const extPath = path.join(__dirname, 'features', ext);
                const module = await import(extPath);
                
                if (module.setup) {
                    await module.setup(this);
                    console.log(`[OK] ${ext}`);
                } else {
                    console.warn(`[WARN] ${ext} has no setup function`);
                }
            } catch (error) {
                console.error(`[FAIL] ${ext}:`, error);
            }
        }
    }
}

const bot = new RealmBot();

// Bot ready event
bot.once('ready', async () => {
    if (!bot.user) {
        console.error('[ERROR] Bot user not found on ready.');
        return;
    }

    console.log('═'.repeat(60));
    console.log(`🌒 ${bot.user.tag} online • ID ${bot.user.id}`);
    console.log(`Guilds: ${bot.guilds.cache.size}  •  Extensions loaded`);
    console.log('═'.repeat(60));

    // Set bot presence
    bot.user.setActivity('the shadows move', { type: ActivityType.Watching });

    // Note: discord.js doesn't have persistent views like Pycord
    // View states are managed through interaction handlers in the cogs
});

// Message handling
bot.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    const WEBHOOK_CHANNEL_ID = '1390426998526181377';
    
    if (message.channel.id !== WEBHOOK_CHANNEL_ID) {
        // Process commands if needed (discord.js v14 uses slash commands primarily)
        return;
    }

    // Handle webhook messages for fitness data sync
    if (message.content.includes('Health data synced for <@')) {
        if (!bot.dbPool) {
            console.error('[ERROR] Database pool not available in messageCreate.');
            return;
        }

        try {
            const userIdMatch = message.content.match(/<@(\d+)>/);
            if (userIdMatch) {
                const userId = userIdMatch[1];
                console.log(`[BOT] Processing webhook for user ${userId}`);
                // Process fitness data here
            }
        } catch (error) {
            console.error('[ERROR] Failed to process webhook:', error);
        }
    }
});

// Error handling
bot.on('error', (error) => {
    console.error('[ERROR] Bot error:', error);
    Sentry.captureException(error);
});

process.on('unhandledRejection', (error) => {
    console.error('[ERROR] Unhandled rejection:', error);
    Sentry.captureException(error);
});

// Main startup function
async function main() {
    if (!TOKEN) {
        console.error('[FAIL] DISCORD_TOKEN not found in environment variables.');
        process.exit(1);
    }

    try {
        console.log('🌒 Starting Realm of Shadows - Dual Mode (Fastify + Discord Bot)');
        console.log('='.repeat(60));

        // Initialize database
        await bot.setupDatabase();

        // Initialize Redis
        await bot.setupRedis();

        // Load extensions
        await bot.loadExtensions();

        // Start Fastify server
        console.log('[INFO] Starting Fastify server...');
        startFastifyServer(bot);

        // Start Discord bot
        console.log('[INFO] Starting Discord bot...');
        await bot.login(TOKEN);
    } catch (error) {
        console.error('[FAIL] Failed to start bot:', error);
        Sentry.captureException(error);
        process.exit(1);
    }
}

// Start the application
main();
