import { Message, EmbedBuilder } from 'discord.js';
import { RealmBot } from '../../main';

/**
 * Quests Cog
 * Handles daily quests, weekly contracts, and quest management
 */
export class QuestsCog {
    private bot: RealmBot;

    constructor(bot: RealmBot) {
        this.bot = bot;
    }

    /**
     * Handle !quests command
     */
    async handleQuestsCommand(message: Message): Promise<void> {
        const user = message.author;

        const embed = new EmbedBuilder()
            .setTitle('📜 Quest Log')
            .setDescription(
                `\`\`\`ansi\n` +
                `[ QUEST SYSTEM ]\n` +
                `──────────────────────────────────────────────\n` +
                `🎭 Operative: ${user.username}\n` +
                `📋 Daily Quests: 0/3\n` +
                `📅 Weekly Contracts: 0/7\n` +
                `──────────────────────────────────────────────\n` +
                `"Your missions await..."\n` +
                `\`\`\``
            )
            .setColor(0xF39C12);

        if (message.channel.isSendable()) {
            await message.channel.send({ embeds: [embed] });
        }
    }

    registerHandlers(): void {
        this.bot.on('messageCreate', async (message) => {
            if (message.author.bot) return;
            if (message.content.toLowerCase() === '!quests') {
                await this.handleQuestsCommand(message);
            }
        });
    }
}

export async function setup(bot: RealmBot): Promise<void> {
    const cog = new QuestsCog(bot);
    cog.registerHandlers();
    console.log('[OK] Quests cog loaded');
}
