"""Storage backends for RootzEngine"""

from .local import LocalStorage
from .azure import AzureStorage

__all__ = ["LocalStorage", "AzureStorage"]
