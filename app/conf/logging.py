import logging
import logging.config
import os

# --- Configuration ---
# Default log directory is "logs"
LOG_DIR = os.getenv("LOG_DIR", "logs")

# Logging level (e.g., INFO, DEBUG, WARNING)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Maximum size of a log file in bytes before it gets rotated
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))  # 10MB

# Number of backup log files to keep
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))


# --- Logging Setup ---
def configure_logging():
    # Ensure the log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    # Define the logging configuration
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,  # Allow other loggers to function
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            # Write logs to a rotating file
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{LOG_DIR}/access.log",
                "maxBytes": LOG_MAX_BYTES,
                "backupCount": LOG_BACKUP_COUNT,
                "formatter": "standard"
            },
            # Output logs to the console
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard"
            }
        },
        # Root logger configuration
        "root": {
            "handlers": ["file", "console"],
            "level": LOG_LEVEL
        }
    }

    # Apply the logging configuration
    logging.config.dictConfig(log_config)
