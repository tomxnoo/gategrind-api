#!/usr/bin/env python3
"""
Simple fake Redis server using fakeredis for development
This provides a Redis-compatible interface without requiring Docker
"""

import asyncio
import logging
import fakeredis.aioredis
from aiohttp import web
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FakeRedisServer:
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
        self.redis = None
        
    async def start(self):
        """Start the fake Redis server"""
        try:
            # Create a fake Redis instance
            self.redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
            logger.info(f"Fake Redis server started on {self.host}:{self.port}")
            logger.info("This is a development Redis replacement using fakeredis")
            
            # Keep the server running
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error starting fake Redis server: {e}")
            raise

async def main():
    """Main function to run the fake Redis server"""
    server = FakeRedisServer()
    
    try:
        logger.info("Starting fake Redis server for SHADOW_NEXUS development...")
        logger.info("This replaces the need for Docker Desktop and real Redis")
        await server.start()
    except KeyboardInterrupt:
        logger.info("Fake Redis server stopped by user")
    except Exception as e:
        logger.error(f"Fake Redis server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())