import { Message, EmbedBuilder } from 'discord.js';
import { RealmBot } from '../../main';

/**
 * Incursions Cog
 * Handles dungeon/incursion system
 */
export class IncursionsCog {
    private bot: RealmBot;

    constructor(bot: RealmBot) {
        this.bot = bot;
    }

    /**
     * Handle !incursions command
     */
    async handleIncursionsCommand(message: Message): Promise<void> {
        const user = message.author;

        const embed = new EmbedBuilder()
            .setTitle('⚔️ Incursions')
            .setDescription(
                `\`\`\`ansi\n` +
                `[ INCURSION SYSTEM ]\n` +
                `──────────────────────────────────────────────\n` +
                `🎭 Operative: ${user.username}\n` +
                `🗡️ Available Dungeons: 0\n` +
                `🏆 Completed: 0\n` +
                `──────────────────────────────────────────────\n` +
                `"The dungeons await..."\n` +
                `\`\`\``
            )
            .setColor(0x8B0000);

        if (message.channel.isSendable()) {
            await message.channel.send({ embeds: [embed] });
        }
    }

    registerHandlers(): void {
        this.bot.on('messageCreate', async (message) => {
            if (message.author.bot) return;
            if (message.content.toLowerCase() === '!incursions') {
                await this.handleIncursionsCommand(message);
            }
        });
    }
}

export async function setup(bot: RealmBot): Promise<void> {
    const cog = new IncursionsCog(bot);
    cog.registerHandlers();
    console.log('[OK] Incursions cog loaded');
}
