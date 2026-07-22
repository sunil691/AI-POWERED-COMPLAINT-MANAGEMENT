"""Production-oriented application logging configuration."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(level: str = "INFO", log_directory: Path = Path("logs")) -> None:
	"""Configure console and rotating file handlers for the application."""
	log_directory.mkdir(parents=True, exist_ok=True)
	numeric_level = getattr(logging, level.upper(), logging.INFO)

	formatter = logging.Formatter(LOG_FORMAT)
	console_handler = logging.StreamHandler()
	console_handler.setFormatter(formatter)

	file_handler = RotatingFileHandler(
		log_directory / "app.log",
		maxBytes=10 * 1024 * 1024,
		backupCount=5,
		encoding="utf-8",
	)
	file_handler.setFormatter(formatter)

	root_logger = logging.getLogger()
	root_logger.setLevel(numeric_level)
	root_logger.handlers.clear()
	root_logger.addHandler(console_handler)
	root_logger.addHandler(file_handler)
