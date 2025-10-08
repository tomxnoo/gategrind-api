import Fastify from 'fastify';
import { RealmBot } from '../main';

export function startFastifyServer(bot: RealmBot): void {
    const fastify = Fastify({ logger: true });
    const port = parseInt(process.env.API_PORT || '8000', 10);

    // Health check endpoint
    fastify.get('/health', async (request, reply) => {
        return { status: 'ok', timestamp: new Date().toISOString() };
    });

    // Start server
    fastify.listen({ port, host: '0.0.0.0' }, (err, address) => {
        if (err) {
            console.error('[FAIL] Fastify server error:', err);
            process.exit(1);
        }
        console.log(`[OK] Fastify server listening on ${address}`);
    });
}
