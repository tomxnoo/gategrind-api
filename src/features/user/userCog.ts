import { Message, EmbedBuilder } from 'discord.js';
import { RealmBot } from '../../main';

/**
 * User Cog
 * Handles user profile, stats, and progression
 */
export class UserCog {
    private bot: RealmBot;

    constructor(bot: RealmBot) {
        this.bot = bot;
    }

    /**
     * Handle !profile command
     */
    async handleProfileCommand(message: Message): Promise<void> {
        const user = message.author;

        const embed = new EmbedBuilder()
            .setTitle('👤 User Profile')
            .setDescription(
                `\`\`\`ansi\n` +
                `[ USER PROFILE ]\n` +
                `──────────────────────────────────────────────\n` +
                `🎭 Operative: ${user.username}\n` +
                `⚡ Level: 1\n` +
                `✨ XP: 0/100\n` +
                `──────────────────────────────────────────────\n` +
                `"Your journey begins..."\n` +
                `\`\`\``
            )
            .setColor(0x1ABC9C);

        if (message.channel.isSendable()) {
            await message.channel.send({ embeds: [embed] });
        }
    }

    registerHandlers(): void {
        this.bot.on('messageCreate', async (message) => {
            if (message.author.bot) return;
            if (message.content.toLowerCase() === '!profile') {
                await this.handleProfileCommand(message);
            }
        });
    }
}

export async function setup(bot: RealmBot): Promise<void> {
    const cog = new UserCog(bot);
    cog.registerHandlers();
    console.log('[OK] User cog loaded');
}
