### Create app/core/config.py

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = Field(
        default="Employee Management API",
        validation_alias="APP_NAME",
    )

    app_env: Literal[
        "development",
        "testing",
        "staging",
        "production",
    ] = Field(
        default="development",
        validation_alias="APP_ENV",
    )

    debug: bool = Field(
        default=False,
        validation_alias="DEBUG",
    )

    log_level: str = Field(
        default="INFO",
        validation_alias="LOG_LEVEL",
    )

    api_prefix: str = Field(
        default="/api",
        validation_alias="API_PREFIX",
    )

    host: str = Field(
        default="127.0.0.1",
        validation_alias="HOST",
    )

    port: int = Field(
        default=8000,
        validation_alias="PORT",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


'''
Explanation
==============
BaseSettings  --> Provides configuration loading and validation.

validation_alias  --> Maps a Python attribute to its corresponding environment variable.

For example:

app_name

reads:
APP_NAME=Employee Management API

Literal
Restricts app_env to the specified values.

If an unsupported environment name is supplied, configuration validation fails instead of silently accepting it.

@lru_cache  --> Caches the settings object so that repeated calls to get_settings() do not repeatedly construct it.

env_file=".env"
Allows local development configuration to be loaded from the .env file.

The process environment takes precedence over values in .env, which is useful when deployment infrastructure injects configuration.

Important production consideration
====================================
The .env file path is relative to the process working directory. If an application is launched from another directory, the file might not be found.

For production, prefer environment variables or a secret manager supplied by the deployment platform. If .env is used in development, run the application from the project root or configure an explicit path.

'''
