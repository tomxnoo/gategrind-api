import redis.asyncio as aioredis
import json

class RedisCache:
    def __init__(self, url: str):
        self.url = url
        self.pool = None

    async def connect(self):
        self.pool = await aioredis.from_url(self.url, decode_responses=True)

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def get(self, key: str):
        if not self.pool:
            raise RuntimeError("Redis pool not initialized")
        return await self.pool.get(key)

    async def set(self, key: str, value, expire: int | None = None):
        if not self.pool:
            raise RuntimeError("Redis pool not initialized")
        await self.pool.set(key, value, ex=expire)

    async def delete(self, key: str):
        if not self.pool:
            raise RuntimeError("Redis pool not initialized")
        await self.pool.delete(key)

async def get_user_json_from_cache(bot, user_id: int):
    cache_key = f"user_json_data:{user_id}"
    cached = await bot.redis.get(cache_key)
    if cached:
        return json.loads(cached)
    async with bot.db_pool.acquire() as conn:
        from core.database import db
        data = await db.get_user_json_data(conn, user_id)
        await bot.redis.set(cache_key, json.dumps(data), expire=3600)
        return data

async def get_or_cache_user_json_data(bot, user_id: int) -> dict:
    cache_key = f"user_json_data:{user_id}"
    user_json = await get_user_json_from_cache(bot, user_id)
    if user_json is None:
        async with bot.db_pool.acquire() as conn:
            from core.database import db
            data = await db.get_user_json_data(conn, user_id)
            await bot.redis.set(cache_key, json.dumps(data), expire=3600)
            return data
    return user_json

async def invalidate_user_json_cache(bot, user_id: int):
    cache_key = f"user_json_data:{user_id}"
    await bot.redis.delete(cache_key)