import { Message, EmbedBuilder } from 'discord.js';
import { RealmBot } from '../../main';

/**
 * Awakening System Cog
 * Handles awakening commands and panel registration
 */
export class AwakeningCog {
    private bot: RealmBot;

    constructor(bot: RealmBot) {
        this.bot = bot;
    }

    /**
     * Handle awakening command
     */
    async handleAwakeningCommand(message: Message): Promise<void> {
        const user = message.author;

        try {
            const embed = new EmbedBuilder()
                .setTitle('🌙 Awakening Ritual')
                .setDescription(
                    `\`\`\`ansi\n` +
                    `[ AWAKENING SYSTEM ]\n` +
                    `──────────────────────────────────────────────\n` +
                    `🎭 Operative: ${user.username}\n` +
                    `✨ Awakening Level: 0\n` +
                    `──────────────────────────────────────────────\n` +
                    `"The shadows call to you..."\n` +
                    `\`\`\``
                )
                .setColor(0x9B59B6); // purple

            if (message.channel.isSendable()) {
                await message.channel.send({ embeds: [embed] });
            }
        } catch (error) {
            console.error('[AWAKENING] Error:', error);
            const errorEmbed = new EmbedBuilder()
                .setTitle('❌ AWAKENING ERROR')
                .setDescription(`\`\`\`\n${error}\n\`\`\``)
                .setColor(0xFF0000);
            if (message.channel.isSendable()) {
                await message.channel.send({ embeds: [errorEmbed] });
            }
        }
    }

    /**
     * Register command handlers
     */
    registerHandlers(): void {
        this.bot.on('messageCreate', async (message) => {
            if (message.author.bot) return;
            const content = message.content.toLowerCase();
            if (content === '!awakening' || content === '!awaken' || content === '!ritual') {
                await this.handleAwakeningCommand(message);
            }
        });
    }
}

/**
 * Setup function to initialize the cog
 */
export async function setup(bot: RealmBot): Promise<void> {
    const cog = new AwakeningCog(bot);
    cog.registerHandlers();
    console.log('[OK] Awakening cog loaded');
}
