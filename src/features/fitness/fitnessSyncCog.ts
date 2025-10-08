import { Message, EmbedBuilder } from 'discord.js';
import { RealmBot } from '../../main';

/**
 * Fitness Sync Cog
 * Handles fitness integration and synchronization
 */
export class FitnessSyncCog {
    private bot: RealmBot;

    constructor(bot: RealmBot) {
        this.bot = bot;
    }

    /**
     * Handle !fitness command
     */
    async handleFitnessCommand(message: Message): Promise<void> {
        const embed = new EmbedBuilder()
            .setTitle('🏃‍♂️ Fitness Integration Hub')
            .setDescription(
                `\`\`\`ansi\n` +
                `[BIOMETRIC SYNC PROTOCOLS]\n` +
                `Available integrations:\n` +
                `🟢 Garmin Connect → !fitness setup garmin\n` +
                `🟡 Apple Health   → Manual export support\n` +
                `🟡 HealthFit      → Manual export support\n\n` +
                `!fitness sync     → Manual sync now\n` +
                `!fitness status   → Check sync status\n` +
                `!fitness disable  → Disable auto-sync\n` +
                `\`\`\``
            )
            .setColor(0x007cc3);

        if (message.channel.isSendable()) {
            await message.channel.send({ embeds: [embed] });
        }
    }

    registerHandlers(): void {
        this.bot.on('messageCreate', async (message) => {
            if (message.author.bot) return;
            if (message.content.toLowerCase().startsWith('!fitness')) {
                await this.handleFitnessCommand(message);
            }
        });
    }
}

export async function setup(bot: RealmBot): Promise<void> {
    const cog = new FitnessSyncCog(bot);
    cog.registerHandlers();
    console.log('[OK] Fitness Sync cog loaded');
}
