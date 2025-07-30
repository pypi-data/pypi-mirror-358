import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Proxar:
    """A Python client for fetching public proxies.

    This library provides an asynchronous, easy-to-use interface to
    retrieve fresh proxies, handling the complexities of web scraping
    and source aggregation.
    """

    def __init__(self) -> None:
        """Initialize the Proxar instance."""
        logger.info("Proxar instance has been initialized.")
