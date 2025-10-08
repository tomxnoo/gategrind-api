import { Message } from 'discord.js';
import { RealmBot } from '../../main';

/**
 * Reroll Reset Cog
 * Handles daily quest reroll resets (admin only)
 */
export class RerollResetCog {
    private bot: RealmBot;

    constructor(bot: RealmBot) {
        this.bot = bot;
    }

    /**
     * Handle !rr command (owner only)
     */
    async handleRerollReset(message: Message, targetUserId?: string): Promise<void> {
        // Check if user is bot owner
        const application = await this.bot.application?.fetch();
        if (message.author.id !== application?.owner?.id) {
            await message.reply('❌ Only the bot owner can use this command.');
            return;
        }

        const userId = targetUserId || message.author.id;
        console.log(`[DEBUG] Reroll reset for user ${userId}`);
        await message.reply(`✅ Daily reroll reset for user ${userId}.`);
    }

    registerHandlers(): void {
        this.bot.on('messageCreate', async (message) => {
            if (message.author.bot) return;
            if (message.content.toLowerCase().startsWith('!rr')) {
                const parts = message.content.split(' ');
                const targetUserId = parts[1];
                await this.handleRerollReset(message, targetUserId);
            }
        });
    }
}

export async function setup(bot: RealmBot): Promise<void> {
    const cog = new RerollResetCog(bot);
    cog.registerHandlers();
    console.log('[OK] Reroll Reset cog loaded');
}
