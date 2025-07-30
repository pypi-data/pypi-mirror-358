import logging
import os

DEFAULT_LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")


def setup_logging(*, timestamp: bool = True) -> None:
    if timestamp:
        logging.basicConfig(
            level=DEFAULT_LOGGING_LEVEL,
            format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        logging.basicConfig(
            level=DEFAULT_LOGGING_LEVEL,
        )
