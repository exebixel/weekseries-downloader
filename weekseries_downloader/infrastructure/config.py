"""
Configuration module for logging and application settings
"""

import logging
import logging.config
import os
from pathlib import Path
from typing import Optional


class LoggingConfig:
    """Centralized logging configuration"""

    @staticmethod
    def setup(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
        """
        Setup logging configuration

        Args:
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file (optional)
        """
        # Create log directory if needed
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

        # Base configuration
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "datefmt": "%Y-%m-%d %H:%M:%S"},
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "simple": {"format": "%(levelname)s - %(message)s"},
            },
            "handlers": {"console": {"class": "logging.StreamHandler", "level": log_level, "formatter": "simple", "stream": "ext://sys.stdout"}},
            "loggers": {"weekseries_downloader": {"level": log_level, "handlers": ["console"], "propagate": False}},
            "root": {"level": log_level, "handlers": ["console"]},
        }

        # Add file handler if specified
        if log_file:
            config["handlers"]["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            }

            # Add file handler to loggers
            config["loggers"]["weekseries_downloader"]["handlers"].append("file")
            config["root"]["handlers"].append("file")

        # Apply configuration
        logging.config.dictConfig(config)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get configured logger

        Args:
            name: Logger name (usually __name__)

        Returns:
            Configured logger
        """
        return logging.getLogger(name)

    @staticmethod
    def setup_from_config_file(config_file: str = "logging.conf") -> None:
        """
        Setup logging from configuration file

        Args:
            config_file: Path to configuration file
        """
        if os.path.exists(config_file):
            # Create log directory if needed
            os.makedirs("logs", exist_ok=True)
            logging.config.fileConfig(config_file, disable_existing_loggers=False)
        else:
            # Fallback to default configuration
            LoggingConfig.setup_default()

    @staticmethod
    def setup_default() -> None:
        """Setup default logging based on environment variables"""

        # Get configuration from environment variables
        log_level = os.getenv("WEEKSERIES_LOG_LEVEL", "INFO").upper()
        log_file = os.getenv("WEEKSERIES_LOG_FILE")

        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_levels:
            log_level = "INFO"

        LoggingConfig.setup(log_level, log_file)


class AppConfig:
    """Application-wide configuration"""

    DEFAULT_TIMEOUT = 30
    DEFAULT_CACHE_TTL = 600  # 10 minutes
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/131.0.0.0 Safari/537.36"

    @staticmethod
    def get_version() -> str:
        """
        Get application version from pyproject.toml

        Returns:
            Version string or "unknown" if not found
        """
        try:
            from pathlib import Path
            import tomllib  # Python 3.11+

            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    return data.get("tool", {}).get("poetry", {}).get("version", "unknown")
        except Exception:
            pass

        return "unknown"


# Auto-configure logging on import
# Try to use config file, otherwise use default configuration
LoggingConfig.setup_from_config_file()
