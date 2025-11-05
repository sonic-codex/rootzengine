import logging
from pathlib import Path
from azure.storage.blob import BlobServiceClient
from rootzengine.core.config import AzureConfig

logger = logging.getLogger(__name__)


class AzureStorageManager:
    def __init__(self, config: AzureConfig):
        self.config = config
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                config.connection_string
            )
            self.container_client = self.blob_service_client.get_container_client(
                config.container_name
            )
            logger.info(
                f"Successfully connected to Azure container: {config.container_name}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Azure Blob Storage: {e}")
            raise

    def upload_file(self, local_path: Path, blob_name: str) -> bool:
        """
        Upload a file to Azure Blob Storage.

        Args:
            local_path: Path to local file
            blob_name: Name for the blob in Azure

        Returns:
            True if successful, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.config.container_name,
                blob=blob_name
            )

            with open(local_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

            logger.info(f"Successfully uploaded {local_path} as {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False

    def download_file(self, blob_name: str, local_path: Path) -> bool:
        """
        Download a file from Azure Blob Storage.

        Args:
            blob_name: Name of the blob in Azure
            local_path: Path where to save the file locally

        Returns:
            True if successful, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.config.container_name,
                blob=blob_name
            )

            # Ensure parent directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)

            with open(local_path, "wb") as download_file:
                download_data = blob_client.download_blob()
                download_file.write(download_data.readall())

            logger.info(f"Successfully downloaded {blob_name} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {blob_name}: {e}")
            return False

    def download_blobs(self, destination_dir: Path, prefix: str = "processed/"):
        """
        Downloads blobs from a specific prefix in the Azure container to a local directory.
        """
        logger.info(f"Listing blobs with prefix '{prefix}'...")
        blobs = self.container_client.list_blobs(name_starts_with=prefix)
        downloaded_count = 0
        for blob in blobs:
            download_path = destination_dir / Path(blob.name).relative_to(Path(prefix).parent)
            download_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Downloading {blob.name} to {download_path}...")
            with open(download_path, "wb") as download_file:
                download_file.write(
                    self.container_client.download_blob(blob.name).readall()
                )
            downloaded_count += 1
        logger.info(f"Successfully downloaded {downloaded_count} files to {destination_dir}.")

    def delete_file(self, blob_name: str) -> bool:
        """
        Delete a file from Azure Blob Storage.

        Args:
            blob_name: Name of the blob to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.config.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            logger.info(f"Successfully deleted {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {blob_name}: {e}")
            return False

    def list_blobs(self, prefix: str = "") -> list:
        """
        List all blobs with a given prefix.

        Args:
            prefix: Prefix to filter blobs

        Returns:
            List of blob names
        """
        try:
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Failed to list blobs: {e}")
            return []