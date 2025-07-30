import logging
from pathlib import Path

import platformdirs

logger = logging.getLogger(__name__)


class StorageHandler:
    """Handle storage operations."""

    def __init__(self, storage_dir: str | Path | None):
        """Initialize the storage handler instance.

        Args:
            storage_dir (str | Path | None): The path to store proxy
                files. If None, a default directory is used based on
                the operating system.
        """
        # Set storage path and ensure its existence
        if storage_dir is None:
            self.storage_path = Path(platformdirs.user_data_dir("proxar"))
        else:
            self.storage_path = Path(storage_dir)

        self.storage_path.mkdir(parents=True, exist_ok=True)

        logger.debug("Storage handler has been initialized.")
