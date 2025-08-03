"""Storage management module."""

from .azure import AzureBlobStorageManager
from .local import LocalStorageManager

__all__ = ["AzureBlobStorageManager", "LocalStorageManager"]