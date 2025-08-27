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