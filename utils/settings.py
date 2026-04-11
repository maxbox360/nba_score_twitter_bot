import logging
import os
import sys


logger = logging.getLogger(__name__)


def configure_logging():
    """Configure application logging for local runs, Docker, and CI."""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, None)
    invalid_level = not isinstance(level, int)
    if invalid_level:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )

    if invalid_level:
        logger.warning(
            "Invalid LOG_LEVEL '%s'. Falling back to INFO.",
            level_name,
        )


def get_env(name):
    try:
        secret = os.getenv(name)
        if not secret:
            logger.warning("Environment variable '%s' is not set.", name)

        return secret

    except Exception:
        logger.exception("Error loading secret '%s'", name)
        return None


