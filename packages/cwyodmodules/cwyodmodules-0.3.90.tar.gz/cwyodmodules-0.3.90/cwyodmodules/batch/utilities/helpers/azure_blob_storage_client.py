import mimetypes
from typing import Optional
from datetime import datetime, timedelta
from azure.storage.blob import (
    generate_blob_sas,
    generate_container_sas,
    ContentSettings,
    UserDelegationKey,
)
from azure.core.credentials import AzureNamedKeyCredential
from azure.storage.queue import BinaryBase64EncodePolicy
import chardet
from .env_helper import EnvHelper
from mgmt_config import logger, identity

# Import the azpaddypy storage abstraction
from azpaddypy.resources.storage import create_azure_storage

env_helper: EnvHelper = EnvHelper()
log_execution = env_helper.LOG_EXECUTION
log_args = env_helper.LOG_ARGS
log_result = env_helper.LOG_RESULT

@logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
def connection_string(account_name: str, account_key: str):
    return f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"


@logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
def create_queue_client():
    """Create a queue client using azpaddypy storage abstraction."""
    env_helper: EnvHelper = EnvHelper()
    
    # Use azpaddypy storage abstraction
    storage = create_azure_storage(
        account_name=env_helper.AZURE_BLOB_ACCOUNT_NAME,
        account_key=env_helper.AZURE_BLOB_ACCOUNT_KEY if env_helper.AZURE_AUTH_TYPE != "rbac" else None,
        container_name=None,  # Not needed for queue operations
        queue_name=env_helper.DOCUMENT_PROCESSING_QUEUE_NAME
    )
    
    # Return the queue client with binary base64 encoding policy
    queue_client = storage.queue_client
    queue_client.message_encode_policy = BinaryBase64EncodePolicy()
    return queue_client


class AzureBlobStorageClient:
    """Compatibility wrapper around azpaddypy AzureStorage abstraction."""
    
    def __init__(
        self,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        container_name: Optional[str] = None,
    ):
        env_helper: EnvHelper = EnvHelper()

        self.auth_type = env_helper.AZURE_AUTH_TYPE
        self.account_name = account_name or env_helper.AZURE_BLOB_ACCOUNT_NAME
        self.container_name = container_name or env_helper.AZURE_BLOB_CONTAINER_NAME
        self.endpoint = env_helper.AZURE_STORAGE_ACCOUNT_ENDPOINT

        # Create azpaddypy storage instance
        self.storage = create_azure_storage(
            account_name=self.account_name,
            account_key=account_key or (env_helper.AZURE_BLOB_ACCOUNT_KEY if self.auth_type != "rbac" else None),
            container_name=self.container_name
        )
        
        # Keep references for compatibility with existing code
        self.blob_service_client = self.storage.blob_service_client
        self.account_key = account_key or (env_helper.AZURE_BLOB_ACCOUNT_KEY if self.auth_type != "rbac" else None)
        
        # Handle user delegation key for RBAC
        if self.auth_type == "rbac":
            self.user_delegation_key = self.request_user_delegation_key(
                blob_service_client=self.blob_service_client
            )
        else:
            self.user_delegation_key = None

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def request_user_delegation_key(
        self, blob_service_client
    ) -> UserDelegationKey:
        # Get a user delegation key that's valid for 1 day
        delegation_key_start_time = datetime.utcnow()
        delegation_key_expiry_time = delegation_key_start_time + timedelta(days=1)

        user_delegation_key = blob_service_client.get_user_delegation_key(
            key_start_time=delegation_key_start_time,
            key_expiry_time=delegation_key_expiry_time,
        )
        return user_delegation_key

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def file_exists(self, file_name):
        """Check if a blob exists."""
        try:
            # Use azpaddypy storage abstraction
            self.storage.download_blob(file_name)
            return True
        except Exception:
            return False

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def upload_file(
        self,
        bytes_data,
        file_name,
        content_type: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ):
        """Upload a file using azpaddypy storage abstraction."""
        # Handle content type detection
        if content_type is None:
            content_type = mimetypes.MimeTypes().guess_type(file_name)[0]
            charset = (
                f"; charset={chardet.detect(bytes_data)['encoding']}"
                if content_type == "text/plain"
                else ""
            )
            content_type = content_type if content_type is not None else "text/plain"
            content_type = content_type + charset

        # Upload using azpaddypy abstraction
        self.storage.upload_blob(
            blob_name=file_name,
            data=bytes_data,
            overwrite=True,
            content_type=content_type,
            metadata=metadata
        )
        
        # Generate and return SAS URL
        return (
            f"{self.endpoint}{self.container_name}/{file_name}"
            + "?"
            + generate_blob_sas(
                self.account_name,
                self.container_name,
                file_name,
                user_delegation_key=self.user_delegation_key,
                account_key=self.account_key,
                permission="r",
                expiry=datetime.utcnow() + timedelta(hours=3),
            )
        )

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def download_file(self, file_name):
        """Download a file using azpaddypy storage abstraction."""
        return self.storage.download_blob(file_name)

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def delete_file(self, file_name):
        """Delete a file using azpaddypy storage abstraction."""
        try:
            self.storage.delete_blob(file_name)
        except Exception:
            # Ignore if file doesn't exist
            pass

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def delete_files(self, files, integrated_vectorization: bool):
        """Delete multiple files using azpaddypy storage abstraction."""
        for filename, ids in files.items():
            if not integrated_vectorization:
                filename = filename.split("/")[-1]
            self.delete_file(filename)

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def get_all_files(self):
        """Get all files using azpaddypy storage abstraction."""
        # Use azpaddypy to list blobs
        blob_list = self.storage.list_blobs(include_metadata=True)
        
        # Generate container SAS
        sas = generate_container_sas(
            self.account_name,
            self.container_name,
            user_delegation_key=self.user_delegation_key,
            account_key=self.account_key,
            permission="r",
            expiry=datetime.utcnow() + timedelta(hours=3),
        )
        
        files = []
        converted_files = {}
        
        for blob in blob_list:
            if not blob.name.startswith("converted/"):
                files.append(
                    {
                        "filename": blob.name,
                        "converted": (
                            blob.metadata.get("converted", "false") == "true"
                            if blob.metadata
                            else False
                        ),
                        "embeddings_added": (
                            blob.metadata.get("embeddings_added", "false") == "true"
                            if blob.metadata
                            else False
                        ),
                        "fullpath": f"{self.endpoint}{self.container_name}/{blob.name}?{sas}",
                        "converted_filename": (
                            blob.metadata.get("converted_filename", "")
                            if blob.metadata
                            else ""
                        ),
                        "converted_path": "",
                    }
                )
            else:
                converted_files[blob.name] = (
                    f"{self.endpoint}{self.container_name}/{blob.name}?{sas}"
                )

        for file in files:
            converted_filename = file.pop("converted_filename", "")
            if converted_filename in converted_files:
                file["converted"] = True
                file["converted_path"] = converted_files[converted_filename]

        return files

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def upsert_blob_metadata(self, file_name, metadata):
        """Update blob metadata using the underlying blob client."""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=file_name
        )
        # Read existing metadata
        blob_metadata = blob_client.get_blob_properties().metadata
        # Update metadata
        blob_metadata.update(metadata)
        # Set updated metadata
        blob_client.set_blob_metadata(metadata=blob_metadata)

    def get_container_sas(self):
        """Generate a container SAS URL."""
        return "?" + generate_container_sas(
            account_name=self.account_name,
            container_name=self.container_name,
            user_delegation_key=self.user_delegation_key,
            account_key=self.account_key,
            permission="r",
            expiry=datetime.utcnow() + timedelta(days=365 * 5),
        )

    def get_blob_sas(self, file_name):
        """Generate a blob SAS URL."""
        return (
            f"{self.endpoint}{self.container_name}/{file_name}"
            + "?"
            + generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=file_name,
                user_delegation_key=self.user_delegation_key,
                account_key=self.account_key,
                permission="r",
                expiry=datetime.utcnow() + timedelta(hours=1),
            )
        )
