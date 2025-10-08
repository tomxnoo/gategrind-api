import { Message, EmbedBuilder } from 'discord.js';
import { RealmBot } from '../../main';

/**
 * Buff Tracker Cog
 * Handles buff management, active buffs, and consumable buffs
 */
export class BuffsCog {
    private bot: RealmBot;

    constructor(bot: RealmBot) {
        this.bot = bot;
    }

    /**
     * Handle !buffs command
     */
    async handleBuffsCommand(message: Message): Promise<void> {
        const user = message.author;

        const embed = new EmbedBuilder()
            .setTitle('✨ Buff Panel')
            .setDescription(
                `\`\`\`ansi\n` +
                `[ BUFF SYSTEM ]\n` +
                `──────────────────────────────────────────────\n` +
                `🎭 Operative: ${user.username}\n` +
                `💫 Active Buffs: None\n` +
                `🎒 Consumables: Empty\n` +
                `──────────────────────────────────────────────\n` +
                `"Your power awaits..."\n` +
                `\`\`\``
            )
            .setColor(0xE74C3C);

        if (message.channel.isSendable()) {
            await message.channel.send({ embeds: [embed] });
        }
    }

    registerHandlers(): void {
        this.bot.on('messageCreate', async (message) => {
            if (message.author.bot) return;
            if (message.content.toLowerCase() === '!buffs') {
                await this.handleBuffsCommand(message);
            }
        });
    }
}

export async function setup(bot: RealmBot): Promise<void> {
    const cog = new BuffsCog(bot);
    cog.registerHandlers();
    console.log('[OK] Buffs cog loaded');
}
