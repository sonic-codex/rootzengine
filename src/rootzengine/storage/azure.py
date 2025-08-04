"""Azure Blob Storage management."""

import logging
from pathlib import Path
from typing import List, Union

from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient

from rootzengine.core.config import settings
from rootzengine.core.exceptions import StorageError

logger = logging.getLogger(__name__)


class AzureBlobStorageManager:
    """Manages file operations with Azure Blob Storage."""

    def __init__(
        self,
        connection_string: str = None,
        container_name: str = None,
    ):
        """Initialize the Azure Blob Storage manager.

        Args:
            connection_string: The Azure Storage connection string.
            container_name: The name of the blob container.

        Raises:
            StorageError: If configuration is missing.
        """
        azure_settings = settings.azure
        if not azure_settings:
            raise StorageError("Azure configuration is not set.")

        self.connection_string = connection_string or azure_settings.connection_string
        self.container_name = container_name or azure_settings.container_name

        if not self.connection_string or not self.container_name:
            raise StorageError(
                "Azure connection string and container name must be provided."
            )

        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            self.container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            logger.info(f"Connected to Azure Blob Storage container: {self.container_name}")
        except (ValueError, AzureError) as e:
            logger.error(f"Failed to connect to Azure Blob Storage: {e}")
            raise StorageError(f"Azure connection failed: {e}") from e

    def upload_file(
        self, local_path: Union[str, Path], blob_name: str, overwrite: bool = True
    ):
        """Uploads a local file to Azure Blob Storage.

        Args:
            local_path: The path to the local file to upload.
            blob_name: The name of the blob to create in the container.
            overwrite: Whether to overwrite the blob if it already exists.
        """
        local_path = Path(local_path)
        if not local_path.exists():
            raise StorageError(f"Local file not found for upload: {local_path}")

        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            with open(local_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=overwrite)
            logger.info(f"Uploaded {local_path} to blob: {blob_name}")
        except AzureError as e:
            logger.error(f"Failed to upload {local_path} to {blob_name}: {e}")
            raise StorageError(f"Azure upload failed: {e}") from e

    def download_file(self, blob_name: str, local_path: Union[str, Path]):
        """Downloads a blob to a local file.

        Args:
            blob_name: The name of the blob to download.
            local_path: The local path to save the downloaded file.
        """
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            with open(local_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            logger.info(f"Downloaded blob {blob_name} to {local_path}")
        except AzureError as e:
            logger.error(f"Failed to download {blob_name} to {local_path}: {e}")
            raise StorageError(f"Azure download failed: {e}") from e

    def list_blobs(self, prefix: str = "") -> List[str]:
        """Lists blobs in the container.

        Args:
            prefix: An optional prefix to filter blobs.

        Returns:
            A list of blob names.
        """
        try:
            blob_list = self.container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blob_list]
        except AzureError as e:
            logger.error(f"Failed to list blobs with prefix '{prefix}': {e}")
            raise StorageError(f"Azure list blobs failed: {e}") from e