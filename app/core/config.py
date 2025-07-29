"""
Enhanced configuration management with validation and environment support.

This module provides comprehensive configuration management with:
- Environment-based configuration
- Validation and type safety
- Secret management
- Performance optimization settings
"""
import os
import logging
from typing import Optional, List, Dict, Any
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr, field_validator


logger = logging.getLogger(__name__)


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    url: str = Field(
        default="postgresql+asyncpg://user:password@localhost/ros_db",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    
    pool_size: int = Field(
        default=10,
        env="DB_POOL_SIZE",
        description="Database connection pool size"
    )
    
    max_overflow: int = Field(
        default=20,
        env="DB_MAX_OVERFLOW",
        description="Maximum overflow connections"
    )
    
    pool_timeout: int = Field(
        default=30,
        env="DB_POOL_TIMEOUT",
        description="Pool timeout in seconds"
    )
    
    echo_sql: bool = Field(
        default=False,
        env="DB_ECHO_SQL",
        description="Enable SQL query logging"
    )
    
    @field_validator("url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate and normalize database URL."""
        if not v or not isinstance(v, str):
            raise ValueError("Database URL must be a non-empty string")
        
        # Normalize to asyncpg driver
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        
        return v


class RedisConfig(BaseSettings):
    """Redis configuration settings."""
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    url: Optional[str] = Field(
        default=None,
        env="REDIS_URL",
        description="Redis connection URL"
    )
    
    host: str = Field(
        default="localhost",
        env="REDIS_HOST",
        description="Redis host"
    )
    
    port: int = Field(
        default=6379,
        env="REDIS_PORT",
        description="Redis port"
    )
    
    password: Optional[SecretStr] = Field(
        default=None,
        env="REDIS_PASSWORD",
        description="Redis password"
    )
    
    db: int = Field(
        default=0,
        env="REDIS_DB",
        description="Redis database number"
    )
    
    default_ttl: int = Field(
        default=3600,
        env="REDIS_DEFAULT_TTL",
        description="Default TTL in seconds"
    )
    
    max_connections: int = Field(
        default=20,
        env="REDIS_MAX_CONNECTIONS",
        description="Maximum Redis connections"
    )


class SecurityConfig(BaseSettings):
    """Security configuration settings."""
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    jwt_secret_key: SecretStr = Field(
        ...,
        env="JWT_SECRET_KEY",
        description="JWT signing secret key"
    )
    
    jwt_algorithm: str = Field(
        default="HS256",
        env="JWT_ALGORITHM",
        description="JWT signing algorithm"
    )
    
    jwt_expiration_hours: int = Field(
        default=24,
        env="JWT_EXPIRATION_HOURS",
        description="JWT token expiration in hours"
    )
    
    cors_origins: List[str] = Field(
        default=["*"],
        env="CORS_ORIGINS",
        description="CORS allowed origins"
    )
    
    rate_limit_per_minute: int = Field(
        default=60,
        env="RATE_LIMIT_PER_MINUTE",
        description="Rate limit per minute per IP"
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


class DiscordConfig(BaseSettings):
    """Discord bot configuration settings."""
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    bot_token: Optional[SecretStr] = Field(
        default=None,
        env="DISCORD_BOT_TOKEN",
        description="Discord bot token"
    )
    
    guild_id: Optional[int] = Field(
        default=None,
        env="DISCORD_GUILD_ID",
        description="Discord guild ID for slash commands"
    )
    
    command_prefix: str = Field(
        default="!",
        env="DISCORD_COMMAND_PREFIX",
        description="Discord command prefix"
    )
    
    max_message_length: int = Field(
        default=2000,
        env="DISCORD_MAX_MESSAGE_LENGTH",
        description="Maximum Discord message length"
    )


class ObservabilityConfig(BaseSettings):
    """Observability and monitoring configuration."""
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    sentry_dsn: Optional[str] = Field(
        default=None,
        env="SENTRY_DSN",
        description="Sentry DSN for error tracking"
    )
    
    logfire_token: Optional[SecretStr] = Field(
        default=None,
        env="LOGFIRE_TOKEN",
        description="Logfire token for observability"
    )
    
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level"
    )
    
    enable_metrics: bool = Field(
        default=True,
        env="ENABLE_METRICS",
        description="Enable metrics collection"
    )
    
    metrics_port: int = Field(
        default=8080,
        env="METRICS_PORT",
        description="Metrics server port"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper


class PerformanceConfig(BaseSettings):
    """Performance optimization settings."""
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    cache_enabled: bool = Field(
        default=True,
        env="CACHE_ENABLED",
        description="Enable caching"
    )
    
    async_worker_count: int = Field(
        default=4,
        env="ASYNC_WORKER_COUNT",
        description="Number of async workers"
    )
    
    request_timeout: int = Field(
        default=30,
        env="REQUEST_TIMEOUT",
        description="Request timeout in seconds"
    )
    
    max_request_size: int = Field(
        default=1024 * 1024,  # 1MB
        env="MAX_REQUEST_SIZE",
        description="Maximum request size in bytes"
    )
    
    enable_gzip: bool = Field(
        default=True,
        env="ENABLE_GZIP",
        description="Enable GZIP compression"
    )


class GameConfig(BaseSettings):
    """Game-specific configuration settings."""
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    max_dungeon_level: int = Field(
        default=100,
        env="MAX_DUNGEON_LEVEL",
        description="Maximum dungeon level"
    )
    
    base_aura_requirement: int = Field(
        default=100,
        env="BASE_AURA_REQUIREMENT",
        description="Base aura requirement for dungeons"
    )
    
    aura_scaling_factor: float = Field(
        default=1.5,
        env="AURA_SCALING_FACTOR",
        description="Aura requirement scaling factor"
    )
    
    session_timeout_hours: int = Field(
        default=1,
        env="SESSION_TIMEOUT_HOURS",
        description="Dungeon session timeout in hours"
    )
    
    daily_modifier_reset_hour: int = Field(
        default=0,
        env="DAILY_MODIFIER_RESET_HOUR",
        description="Hour when daily modifiers reset (0-23)"
    )
    
    @field_validator("daily_modifier_reset_hour")
    @classmethod
    def validate_reset_hour(cls, v: int) -> int:
        """Validate reset hour is between 0-23."""
        if not 0 <= v <= 23:
            raise ValueError("Daily modifier reset hour must be between 0-23")
        return v


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = Field(
        default="development",
        env="ENVIRONMENT",
        description="Application environment"
    )
    
    debug: bool = Field(
        default=False,
        env="DEBUG",
        description="Enable debug mode"
    )
    
    # API Settings
    api_title: str = Field(
        default="RoS-TRAE API",
        env="API_TITLE",
        description="API title"
    )
    
    api_version: str = Field(
        default="2.0.0",
        env="API_VERSION",
        description="API version"
    )
    
    api_host: str = Field(
        default="0.0.0.0",
        env="API_HOST",
        description="API host"
    )
    
    api_port: int = Field(
        default=8000,
        env="API_PORT",
        description="API port"
    )
    
    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    game: GameConfig = Field(default_factory=GameConfig)
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "validate_assignment": True,
        "extra": "ignore"
    }
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_envs = {"development", "staging", "production", "testing"}
        if v.lower() not in valid_envs:
            logger.warning(f"Unknown environment '{v}', using 'development'")
            return "development"
        return v.lower()
    
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing."""
        return self.environment == "testing"
    
    def get_database_url(self) -> str:
        """Get the complete database URL."""
        return self.database.url
    
    def get_redis_url(self) -> Optional[str]:
        """Get the complete Redis URL."""
        if self.redis.url:
            return self.redis.url
        
        if self.redis.password:
            return (
                f"redis://:{self.redis.password.get_secret_value()}"
                f"@{self.redis.host}:{self.redis.port}/{self.redis.db}"
            )
        
        return f"redis://{self.redis.host}:{self.redis.port}/{self.redis.db}"
    
    def get_discord_token(self) -> str:
        """Get Discord bot token, raising error if not set."""
        # Fallback to direct env loading for nested settings issue
        if self.discord.bot_token:
            return self.discord.bot_token.get_secret_value()
        
        import os
        from dotenv import load_dotenv
        load_dotenv()  # Ensure .env is loaded
        token = os.getenv("DISCORD_BOT_TOKEN")
        if not token:
            raise ValueError("DISCORD_BOT_TOKEN is required but not set in environment variables")
        return token
    
    def get_jwt_secret_key(self) -> str:
        """Get JWT secret key, raising error if not set."""
        if self.security.jwt_secret_key:
            return self.security.jwt_secret_key.get_secret_value()
        
        import os
        key = os.getenv("JWT_SECRET_KEY")
        if not key:
            raise ValueError("JWT_SECRET_KEY is required but not set in environment variables")
        return key
    
    def configure_logging(self):
        """Configure application logging."""
        logging.basicConfig(
            level=getattr(logging, self.observability.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("app.log") if self.is_production() else logging.NullHandler()
            ]
        )
        
        # Adjust third-party library log levels
        if not self.debug:
            logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
            logging.getLogger("discord").setLevel(logging.WARNING)


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    settings = Settings()
    settings.configure_logging()
    
    # Log configuration summary (without secrets)
    logger.info(f"Application started with environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Database: {settings.database.url.split('@')[-1] if '@' in settings.database.url else 'local'}")
    logger.info(f"Redis: {'enabled' if settings.redis.url or settings.redis.host != 'localhost' else 'local'}")
    
    return settings