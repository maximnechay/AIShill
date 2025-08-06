import os
from typing import Optional
from pydantic import BaseSettings, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    api_key: str = "xinvest-dev-key-2024"  # Default dev key
    require_auth: bool = False  # Set to True in production

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"  # Cost-effective model
    openai_timeout: int = 30

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Rate Limiting (requests per minute)
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10

    # Reply Generation Settings
    default_temperature: float = 0.7
    max_reply_length: int = 600
    min_reply_length: int = 10
    max_char_length: int = 280
    # Monitoring & Logging
    log_level: str = "INFO"
    enable_metrics: bool = True

    # Database (optional - for statistics storage)
    mongo_uri: Optional[str] = None
    enable_database: bool = False

    @validator("openai_api_key")
    def validate_openai_key(cls, v):
        if not v or len(v) < 20:
            raise ValueError("Valid OpenAI API key is required")
        return v

    @validator("openai_model")
    def validate_model(cls, v):
        allowed_models = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ]
        if v not in allowed_models:
            raise ValueError(f"Model must be one of: {', '.join(allowed_models)}")
        return v

    @validator("default_temperature")
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

        # Environment variable mappings
        fields = {
            "openai_api_key": {"env": "OPENAI_API_KEY"},
            "openai_model": {"env": "OPENAI_MODEL"},
            "api_key": {"env": "XINVEST_API_KEY"},
            "require_auth": {"env": "REQUIRE_AUTH"},
            "host": {"env": "HOST"},
            "port": {"env": "PORT"},
            "debug": {"env": "DEBUG"},
            "mongo_uri": {"env": "MONGO_URI"},
            "log_level": {"env": "LOG_LEVEL"},
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


def get_environment_info() -> dict:
    """Get information about the current environment"""
    settings = get_settings()

    return {
        "environment": "development" if settings.debug else "production",
        "openai_model": settings.openai_model,
        "authentication_required": settings.require_auth,
        "database_enabled": settings.enable_database,
        "rate_limiting": {
            "requests_per_minute": settings.rate_limit_per_minute,
            "burst_limit": settings.rate_limit_burst,
        },
        "server": {
            "host": settings.host,
            "port": settings.port,
            "debug_mode": settings.debug,
        },
    }


# Configuration presets for different deployment scenarios
class DeploymentConfig:
    """Predefined configurations for different deployment scenarios"""

    @staticmethod
    def development():
        """Development environment configuration"""
        return {
            "DEBUG": "true",
            "REQUIRE_AUTH": "false",
            "LOG_LEVEL": "DEBUG",
            "OPENAI_MODEL": "gpt-4o-mini",  # Cheaper for testing
            "RATE_LIMIT_PER_MINUTE": "100",
        }

    @staticmethod
    def production():
        """Production environment configuration"""
        return {
            "DEBUG": "false",
            "REQUIRE_AUTH": "true",
            "LOG_LEVEL": "INFO",
            "OPENAI_MODEL": "gpt-4o",  # Better quality for production
            "RATE_LIMIT_PER_MINUTE": "60",
        }

    @staticmethod
    def testing():
        """Testing environment configuration"""
        return {
            "DEBUG": "true",
            "REQUIRE_AUTH": "false",
            "LOG_LEVEL": "WARNING",
            "OPENAI_MODEL": "gpt-3.5-turbo",  # Fastest for tests
            "RATE_LIMIT_PER_MINUTE": "200",
        }


def create_env_file(
    deployment_type: str = "development", openai_key: str = "", api_key: str = ""
) -> str:
    """Create a .env file with specified configuration"""

    if deployment_type == "production":
        config = DeploymentConfig.production()
    elif deployment_type == "testing":
        config = DeploymentConfig.testing()
    else:
        config = DeploymentConfig.development()

    env_content = f"""# XinvestAI Reply Generator Configuration
# Generated for {deployment_type} environment

# OpenAI Configuration
OPENAI_API_KEY={openai_key}
OPENAI_MODEL={config['OPENAI_MODEL']}

# API Security  
XINVEST_API_KEY={api_key or 'xinvest-dev-key-2024'}
REQUIRE_AUTH={config['REQUIRE_AUTH']}

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG={config['DEBUG']}
LOG_LEVEL={config['LOG_LEVEL']}

# Rate Limiting
RATE_LIMIT_PER_MINUTE={config['RATE_LIMIT_PER_MINUTE']}

# Optional: Database for statistics (leave empty to disable)
MONGO_URI=

# Optional: Telegram Integration (for future features)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHANNEL_ID=
"""

    with open(".env", "w") as f:
        f.write(env_content)

    return f".env file created for {deployment_type} environment"


if __name__ == "__main__":
    """CLI for environment setup"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "create-env":
            deployment = sys.argv[2] if len(sys.argv) > 2 else "development"
            openai_key = input("Enter your OpenAI API key: ").strip()
            api_key = input("Enter API key for your service (optional): ").strip()

            result = create_env_file(deployment, openai_key, api_key)
            print(result)

        elif command == "check":
            try:
                settings = get_settings()
                print("✅ Configuration is valid!")
                print(f"🤖 OpenAI Model: {settings.openai_model}")
                print(f"🔐 Auth Required: {settings.require_auth}")
                print(f"🌐 Server: {settings.host}:{settings.port}")
                print(f"📊 Debug Mode: {settings.debug}")
            except Exception as e:
                print(f"❌ Configuration error: {e}")

        elif command == "info":
            try:
                info = get_environment_info()
                print("📋 Environment Information:")
                for key, value in info.items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for sub_key, sub_value in value.items():
                            print(f"    {sub_key}: {sub_value}")
                    else:
                        print(f"  {key}: {value}")
            except Exception as e:
                print(f"❌ Error getting environment info: {e}")
        else:
            print("Usage: python config.py [create-env|check|info]")
    else:
        print("Available commands:")
        print("  create-env [development|production|testing] - Create .env file")
        print("  check - Validate current configuration")
        print("  info - Show environment information")
