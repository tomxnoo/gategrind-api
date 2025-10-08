import { User, EmbedBuilder } from 'discord.js';

/**
 * Get system status header for a user
 */
export function getSystemStatusHeader(user: User): string {
    const username = user.username.toUpperCase();
    return `[0;2m[SHADOW NEXUS][0m [0;1;37m${username}[0m [0;32m●[0m ONLINE`;
}

/**
 * Render a loading embed with animated dots
 */
export function renderLoadingEmbed(user: User, dotCount: number = 1): EmbedBuilder {
    const dots = '.'.repeat(dotCount);
    const header = getSystemStatusHeader(user).replace('```ansi', '').replace('```', '').trim();
    
    const embed = new EmbedBuilder()
        .setDescription(
            `\`\`\`ansi\n${header}\n` +
            `[ PROCESSING REQUEST ]\n` +
            `──────────────────────────────────────────────\n` +
            `⏳ Loading${dots}\n` +
            `\`\`\``
        )
        .setColor(0x2b2d31)
        .setFooter({ text: 'Watcher Console Uplink • Processing' });
    
    return embed;
}

/**
 * Flavor lines for quest completions
 */
export const COMPLETION_FLAVOR_LINES = [
    "The pact is sealed. Shadows stir.",
    "You bow before no fate.",
    "A burden lifted, a soul sharpened.",
    "The ink dries. The contract ends.",
    "You are forged, not found.",
    "Ashes whisper your name.",
    "From shadow, resolve.",
    "Only ghosts remain behind your steps.",
    "You reap what others fear to sow.",
    "Not all who kneel are broken."
];

/**
 * Get a random flavor line
 */
export function getRandomFlavorLine(): string {
    return COMPLETION_FLAVOR_LINES[Math.floor(Math.random() * COMPLETION_FLAVOR_LINES.length)];
}
