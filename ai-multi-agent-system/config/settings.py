"""
Configuration Module
Manages all application settings and environment variables
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI Configuration"""
    api_key: str = Field(..., env="AZURE_OPENAI_API_KEY")
    endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    deployment_name: str = Field(..., env="AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version: str = Field(default="2024-02-15-preview", env="AZURE_OPENAI_API_VERSION")
    model: str = Field(default="gpt-4", env="AZURE_OPENAI_MODEL")

    class Config:
        env_file = ".env"
        case_sensitive = False


class IDITAPISettings(BaseSettings):
    """IDIT API Configuration"""
    base_url: str = Field(..., env="IDIT_API_BASE_URL")
    api_key: str = Field(..., env="IDIT_API_KEY")
    timeout: int = Field(default=30, env="IDIT_API_TIMEOUT")

    class Config:
        env_file = ".env"
        case_sensitive = False


class EmailSettings(BaseSettings):
    """Email Channel Configuration"""
    imap_server: str = Field(..., env="EMAIL_IMAP_SERVER")
    imap_port: int = Field(default=993, env="EMAIL_IMAP_PORT")
    username: str = Field(..., env="EMAIL_USERNAME")
    password: str = Field(..., env="EMAIL_PASSWORD")
    smtp_server: str = Field(..., env="EMAIL_SMTP_SERVER")
    smtp_port: int = Field(default=587, env="EMAIL_SMTP_PORT")

    class Config:
        env_file = ".env"
        case_sensitive = False


class WhatsAppSettings(BaseSettings):
    """WhatsApp Channel Configuration"""
    api_url: str = Field(..., env="WHATSAPP_API_URL")
    access_token: str = Field(..., env="WHATSAPP_ACCESS_TOKEN")
    phone_number_id: str = Field(..., env="WHATSAPP_PHONE_NUMBER_ID")
    business_account_id: str = Field(..., env="WHATSAPP_BUSINESS_ACCOUNT_ID")

    class Config:
        env_file = ".env"
        case_sensitive = False


class TeamsSettings(BaseSettings):
    """Teams Channel Configuration"""
    webhook_url: str = Field(..., env="TEAMS_WEBHOOK_URL")
    bot_id: Optional[str] = Field(None, env="TEAMS_BOT_ID")
    bot_password: Optional[str] = Field(None, env="TEAMS_BOT_PASSWORD")
    app_id: Optional[str] = Field(None, env="TEAMS_APP_ID")

    class Config:
        env_file = ".env"
        case_sensitive = False


class AppSettings(BaseSettings):
    """Application Configuration"""
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    message_poll_interval: int = Field(default=60, env="MESSAGE_POLL_INTERVAL")
    max_concurrent_tasks: int = Field(default=5, env="MAX_CONCURRENT_TASKS")
    enable_retry: bool = Field(default=True, env="ENABLE_RETRY")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    redis_host: Optional[str] = Field(None, env="REDIS_HOST")
    redis_port: Optional[int] = Field(None, env="REDIS_PORT")

    class Config:
        env_file = ".env"
        case_sensitive = False


class Settings:
    """Main Settings Container"""
    def __init__(self):
        self.azure_openai = AzureOpenAISettings()
        self.idit_api = IDITAPISettings()
        self.email = EmailSettings()
        self.whatsapp = WhatsAppSettings()
        self.teams = TeamsSettings()
        self.app = AppSettings()


# Global settings instance
settings = Settings()
