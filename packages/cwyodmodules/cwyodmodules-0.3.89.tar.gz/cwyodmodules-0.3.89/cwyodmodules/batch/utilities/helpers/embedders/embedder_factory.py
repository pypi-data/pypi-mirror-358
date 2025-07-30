from ..env_helper import EnvHelper
from ..azure_blob_storage_client import AzureBlobStorageClient
from .postgres_embedder import PostgresEmbedder


class EmbedderFactory:
    @staticmethod
    def create(env_helper: EnvHelper):
        """
        Creates and returns a PostgreSQL embedder instance.
        
        Args:
            env_helper (EnvHelper): Environment helper instance
            
        Returns:
            PostgresEmbedder: PostgreSQL embedder instance
        """
        return PostgresEmbedder(AzureBlobStorageClient(), env_helper)
