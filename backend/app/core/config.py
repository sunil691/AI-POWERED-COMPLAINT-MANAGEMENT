"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	"""Strongly typed settings shared by application components."""

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		case_sensitive=False,
		extra="ignore",
	)

	app_name: str = "AI-Powered Customer Complaint Management System"
	app_version: str = "0.1.0"
	environment: str = "development"
	debug: bool = False
	database_url: str = Field(
		default="postgresql+psycopg://postgres:postgres@localhost:5432/complaints",
		min_length=1,
	)
	groq_api_key: str = ""
	model_name: str = "llama-3.1-8b-instant"
	upload_directory: Path = Path("uploads")
	max_upload_size: int = Field(default=10 * 1024 * 1024, gt=0)
	allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
	log_level: str = "INFO"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	"""Return the process-wide settings instance."""
	return Settings()


settings = get_settings()
