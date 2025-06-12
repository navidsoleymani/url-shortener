import logging
import logging.config
import os

# --- Configuration ---
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))


# --- Logging Setup ---
def configure_logging():
    os.makedirs(LOG_DIR, exist_ok=True)

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{LOG_DIR}/access.log",
                "maxBytes": LOG_MAX_BYTES,
                "backupCount": LOG_BACKUP_COUNT,
                "formatter": "standard"
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard"
            }
        },
        "root": {
            "handlers": ["file", "console"],
            "level": LOG_LEVEL
        }
    }

    logging.config.dictConfig(log_config)
