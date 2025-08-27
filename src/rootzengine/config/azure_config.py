from azure.storage.blob import BlobServiceClient

class AzureConfig:
    """Handles Azure Blob storage interactions."""
    def __init__(self, conn_str, env='dev'):
        self.conn_str = conn_str
        self.env = env
        self.client = BlobServiceClient.from_connection_string(self.conn_str)

    @property
    def audio_container(self):
        return f'{self.env}-audio'

    @property
    def results_container(self):
        return f'{self.env}-results'

    def upload_blob(self, container, blob_name, data):
        blob_client = self.client.get_blob_client(container=container, blob=blob_name)
        blob_client.upload_blob(data, overwrite=True)

    # ... add lifecycle & switchable client for AKS or Azure ML ...
