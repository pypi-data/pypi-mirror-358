import logging
from pathlib import Path

from .handlers.storage import StorageHandler

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Proxar:
    """A Python client for fetching public proxies.

    This library provides an asynchronous, easy-to-use interface to
    retrieve fresh proxies, handling the complexities of web scraping
    and source aggregation.
    """

    def __init__(self, storage_dir: str | Path | None = None):
        """Initialize the Proxar instance.

        Args:
            storage_dir (str | Path | None): The path to store proxy
                files. Defaults to None.
        """
        self.storage_manager = StorageHandler(storage_dir)
        logger.info("Proxar has been initialized.")
