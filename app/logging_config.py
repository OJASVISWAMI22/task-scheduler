import os

from dotenv import load_dotenv

from logging.config import dictConfig

load_dotenv()

# Logging config for fastapi app
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # To keep uvicorn error visible too
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {  # what to do with message print on terminal , send mail or store in file
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "default",
        },
    },
    "loggers": {  # what logger to use our custom or uvicorn one
        "my_app": {
            "handlers": ["console", "file"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    dictConfig(LOGGING_CONFIG)
