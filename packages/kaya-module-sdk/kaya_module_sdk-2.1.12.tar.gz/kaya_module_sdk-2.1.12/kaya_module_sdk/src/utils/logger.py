import logging
import logging.config


def setup_logging(name: str | int, level: str, location: str | None = None) -> bool:
    if not isinstance(name, str) or level not in (
        "CRITICAL",
        "ERROR",
        "WARNING",
        "INFO",
        "DEBUG",
        "NOTSET",
    ):
        return False
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "default": {
                "level": level,
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
            "file": {
                "level": level,
                "formatter": "standard",
                "class": "logging.FileHandler",
                "filename": ("/var/log" if not location else location) + f"/{name}.log",
                "mode": "a",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["default", "file"],
                "level": level,
                "propagate": True,
            },
            name: {"handlers": ["default", "file"], "level": level, "propagate": True},
        },
    }

    logging.config.dictConfig(logging_config)
    return True
