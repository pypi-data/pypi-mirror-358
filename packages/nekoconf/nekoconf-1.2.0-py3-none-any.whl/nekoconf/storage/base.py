"""Abstract base class for storage backends."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class StorageBackend(ABC):
    """Abstract base class for configuration storage backends.

    This defines the interface that all storage backends must implement.
    Following the Strategy pattern, different backends can be plugged in
    to provide different storage mechanisms.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the storage backend.

        Args:
            logger: Optional logger instance for logging messages
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # List of callback functions to be called on configuration changes
        self.callbacks: List[callable] = []

    def __str__(self):
        return f"{self.__class__.__name__}(backend)"

    @classmethod
    def create(cls, **kwargs):
        """Create a backend instance with configuration.

        This is a convenience method that subclasses can override
        to provide a cleaner creation interface.

        Args:
            **kwargs: Backend-specific configuration

        Returns:
            Configured backend instance
        """
        return cls(**kwargs)

    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """Load configuration data from the storage backend.

        Returns:
            Dictionary containing the configuration data

        Raises:
            StorageError: If loading fails
        """
        pass

    @abstractmethod
    def save(self, data: Dict[str, Any]) -> bool:
        """Save configuration data to the storage backend.

        Args:
            data: Configuration data to save

        Returns:
            True if save was successful, False otherwise
        """
        pass

    def cleanup(self) -> None:
        """Clean up resources used by the storage backend.

        This method is called when the configuration manager is being destroyed.
        Subclasses should override this if they need to clean up resources.
        """
        pass

    def reload(self) -> Dict[str, Any]:
        """Reload configuration from the storage backend.

        By default, this just calls load(), but some backends may
        implement more sophisticated reload logic.

        Returns:
            Dictionary containing the reloaded configuration data
        """
        return self.load()

    def set_change_callback(self, callback: callable) -> None:
        """Register a callback to be called on configuration changes.

        Args:
            callback: Function to call when configuration changes
        """
        if callable(callback):
            self.callbacks.append(callback)
        else:
            self.logger.warning(f"Provided callback is not callable, got: {type(callback)} instead")

    def unset_change_callback(self, callback: callable) -> None:
        """Unregister a previously set change callback.

        Args:
            callback: Function to remove from the change callbacks
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
        else:
            self.logger.warning(f"Provided callback is not callable, got: {type(callback)} instead")


class StorageError(Exception):
    """Exception raised when storage operations fail."""

    pass
