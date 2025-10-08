import { Message, EmbedBuilder, ActionRowBuilder, StringSelectMenuBuilder, StringSelectMenuOptionBuilder } from 'discord.js';
import { RealmBot } from '../../main';
import { getSystemStatusHeader } from '../../shared/utils/headers';

/**
 * System Hub Cog - Main navigation hub for the bot
 */
export class SystemHubCog {
    private bot: RealmBot;

    constructor(bot: RealmBot) {
        this.bot = bot;
    }

    /**
     * Handle !hub command
     */
    async handleHubCommand(message: Message): Promise<void> {
        console.log(`[DEBUG] !hub command called by ${message.author.tag} in ${message.channel}`);
        const user = message.author;

        // Create universal panel style embed
        const header = getSystemStatusHeader(user).replace(/```ansi/g, '').replace(/```/g, '').trim();
        const description = 
            `\`\`\`ansi\n${header}\n[ SHADOW NEXUS MAINFRAME ]\n` +
            `──────────────────────────────────────────────\n` +
            `😈 Open System Hub    → Begin your journey\n` +
            `🔁 Reopen System Hub  → Return to the nexus\n` +
            `──────────────────────────────────────────────\n` +
            `"You place your hand upon the terminal."\n` +
            `\`\`\``;

        const embed = new EmbedBuilder()
            .setDescription(description)
            .setColor(0x2B5B5A) // dark_teal equivalent
            .setFooter({ text: 'Watcher Console Uplink • Stable' });

        // Create select menu for system hub
        const selectMenu = new StringSelectMenuBuilder()
            .setCustomId(`system_public:${user.id}`)
            .setPlaceholder('Initialize Shadow Nexus…')
            .addOptions(
                new StringSelectMenuOptionBuilder()
                    .setLabel('Open System Hub')
                    .setValue('open_hub')
                    .setEmoji('😈'),
                new StringSelectMenuOptionBuilder()
                    .setLabel('Reopen System Hub')
                    .setValue('reopen_hub')
                    .setEmoji('🔁')
            );

        const row = new ActionRowBuilder<StringSelectMenuBuilder>()
            .addComponents(selectMenu);

        try {
            if (message.channel.isSendable()) {
                const sentMessage = await message.channel.send({
                    embeds: [embed],
                    components: [row]
                });
                console.log(`[DEBUG] Message sent successfully - Message ID: ${sentMessage.id}`);
            }
        } catch (error) {
            console.error('[DEBUG] Error sending message:', error);
        }
        
        console.log('[DEBUG] !hub command completed');
    }

    /**
     * Register command handlers
     */
    registerHandlers(): void {
        this.bot.on('messageCreate', async (message) => {
            if (message.author.bot) return;
            if (message.content.toLowerCase() === '!hub') {
                await this.handleHubCommand(message);
            }
        });

        // Handle select menu interactions
        this.bot.on('interactionCreate', async (interaction) => {
            if (!interaction.isStringSelectMenu()) return;
            if (!interaction.customId.startsWith('system_public:')) return;

            const userId = interaction.customId.split(':')[1];
            if (userId && interaction.user.id !== userId) {
                await interaction.reply({ content: 'This is not your menu.', ephemeral: true });
                return;
            }

            const value = interaction.values[0];
            
            if (value === 'open_hub' || value === 'reopen_hub') {
                // Import and show the full system hub view
                const { renderHubEmbed } = await import('./ui/systemHubView');
                const hubEmbed = await renderHubEmbed(this.bot, interaction.user);
                
                // For now, send ephemeral response - full panel implementation would go here
                await interaction.reply({ 
                    embeds: [hubEmbed], 
                    ephemeral: true 
                });
            }
        });
    }
}

/**
 * Setup function to initialize the cog
 */
export async function setup(bot: RealmBot): Promise<void> {
    const cog = new SystemHubCog(bot);
    cog.registerHandlers();
    console.log('[OK] System Hub cog loaded');
}
