from typing import Optional, Dict, Any, Union, List, BinaryIO
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.storage.fileshare import ShareServiceClient, ShareClient, ShareFileClient
from azure.storage.queue import QueueServiceClient, QueueClient
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError, ResourceExistsError
from azure.core.credentials import TokenCredential
from ..mgmt.logging import AzureLogger
from ..mgmt.identity import AzureIdentity
import io
from datetime import datetime


# Storage instance caching
_storage_instances: Dict[Any, "AzureStorage"] = {}


class AzureStorage:
    """Azure Storage Account management with comprehensive blob, file, and queue operations.

    Provides standardized Azure Storage operations using Azure SDK clients
    with integrated logging, error handling, and OpenTelemetry tracing support.
    Supports operations for blob storage, file shares, and queues with proper
    authentication and authorization handling. Container and queue creation
    is handled by infrastructure as code.

    Attributes:
        account_url: Azure Storage Account URL
        service_name: Service identifier for logging and tracing
        service_version: Service version for context
        logger: AzureLogger instance for structured logging
        credential: Azure credential for authentication
        blob_service_client: Azure Blob Service Client instance
        file_service_client: Azure File Share Service Client instance
        queue_service_client: Azure Queue Service Client instance
    """

    def __init__(
        self,
        account_url: str,
        credential: Optional[TokenCredential] = None,
        azure_identity: Optional[AzureIdentity] = None,
        service_name: str = "azure_storage",
        service_version: str = "1.0.0",
        logger: Optional[AzureLogger] = None,
        connection_string: Optional[str] = None,
        enable_blob_storage: bool = True,
        enable_file_storage: bool = True,
        enable_queue_storage: bool = True,
    ):
        """Initialize Azure Storage with comprehensive configuration.

        Args:
            account_url: Azure Storage Account URL (e.g., https://account.blob.core.windows.net/)
            credential: Azure credential for authentication
            azure_identity: AzureIdentity instance for credential management
            service_name: Service name for tracing context
            service_version: Service version for metadata
            logger: Optional AzureLogger instance
            connection_string: Application Insights connection string
            enable_blob_storage: Enable blob storage operations client
            enable_file_storage: Enable file storage operations client
            enable_queue_storage: Enable queue storage operations client

        Raises:
            ValueError: If neither credential nor azure_identity is provided
            Exception: If client initialization fails
        """
        self.account_url = account_url
        self.service_name = service_name
        self.service_version = service_version
        self.enable_blob_storage = enable_blob_storage
        self.enable_file_storage = enable_file_storage
        self.enable_queue_storage = enable_queue_storage

        # Initialize logger - use provided instance or create new one
        if logger is not None:
            self.logger = logger
        else:
            self.logger = AzureLogger(
                service_name=service_name,
                service_version=service_version,
                connection_string=connection_string,
                enable_console_logging=True,
            )

        # Setup credential
        if azure_identity is not None:
            self.credential = azure_identity.get_credential()
            self.azure_identity = azure_identity
        elif credential is not None:
            self.credential = credential
            self.azure_identity = None
        else:
            raise ValueError("Either 'credential' or 'azure_identity' must be provided")

        # Initialize clients
        self.blob_service_client = None
        self.file_service_client = None
        self.queue_service_client = None
        
        self._setup_clients()

        self.logger.info(
            f"Azure Storage initialized for service '{service_name}' v{service_version}",
            extra={
                "account_url": account_url,
                "blob_enabled": enable_blob_storage,
                "file_enabled": enable_file_storage,
                "queue_enabled": enable_queue_storage,
            }
        )

    def _setup_clients(self):
        """Initialize Storage clients based on enabled features.

        Raises:
            Exception: If client initialization fails
        """
        try:
            if self.enable_blob_storage:
                self.blob_service_client = BlobServiceClient(
                    account_url=self.account_url,
                    credential=self.credential
                )
                self.logger.debug("BlobServiceClient initialized successfully")

            if self.enable_file_storage:
                # Convert blob URL to file URL
                file_url = self.account_url.replace('.blob.', '.file.')
                self.file_service_client = ShareServiceClient(
                    account_url=file_url,
                    credential=self.credential,
                    token_intent='backup'
                )
                self.logger.debug("ShareServiceClient initialized successfully")

            if self.enable_queue_storage:
                # Convert blob URL to queue URL
                queue_url = self.account_url.replace('.blob.', '.queue.')
                self.queue_service_client = QueueServiceClient(
                    account_url=queue_url,
                    credential=self.credential
                )
                self.logger.debug("QueueServiceClient initialized successfully")

        except Exception as e:
            self.logger.error(
                f"Failed to initialize Storage clients: {e}",
                exc_info=True
            )
            raise

    # Blob Storage Operations
    def upload_blob(
        self,
        container_name: str,
        blob_name: str,
        data: Union[bytes, str, BinaryIO],
        overwrite: bool = False,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Upload a blob to Azure Blob Storage.

        Args:
            container_name: Name of the container
            blob_name: Name of the blob
            data: Data to upload (bytes, string, or file-like object)
            overwrite: Whether to overwrite existing blob
            metadata: Optional metadata for the blob
            content_type: Optional content type for the blob
            **kwargs: Additional parameters for blob upload

        Returns:
            True if blob was uploaded successfully

        Raises:
            RuntimeError: If blob service client is not initialized
            Exception: If blob upload fails
        """
        with self.logger.create_span(
            "AzureStorage.upload_blob",
            attributes={
                "service.name": self.service_name,
                "operation.type": "blob_upload",
                "storage.container_name": container_name,
                "storage.blob_name": blob_name,
                "storage.account_url": self.account_url
            }
        ):
            if self.blob_service_client is None:
                error_msg = "Blob service client not initialized. Enable blob storage during initialization."
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

            try:
                self.logger.debug(
                    "Uploading blob to Azure Storage",
                    extra={
                        "container_name": container_name,
                        "blob_name": blob_name,
                        "overwrite": overwrite,
                        "has_metadata": metadata is not None,
                        "content_type": content_type
                    }
                )

                blob_client = self.blob_service_client.get_blob_client(
                    container=container_name,
                    blob=blob_name
                )

                blob_client.upload_blob(
                    data,
                    overwrite=overwrite,
                    metadata=metadata,
                    content_type=content_type,
                    **kwargs
                )
                
                self.logger.info(
                    "Blob uploaded successfully",
                    extra={
                        "container_name": container_name,
                        "blob_name": blob_name,
                        "overwrite": overwrite
                    }
                )
                
                return True

            except Exception as e:
                self.logger.error(
                    f"Failed to upload blob '{blob_name}': {e}",
                    extra={
                        "container_name": container_name,
                        "blob_name": blob_name
                    },
                    exc_info=True
                )
                raise

    def download_blob(
        self,
        container_name: str,
        blob_name: str,
        **kwargs
    ) -> Optional[bytes]:
        """Download a blob from Azure Blob Storage.

        Args:
            container_name: Name of the container
            blob_name: Name of the blob
            **kwargs: Additional parameters for blob download

        Returns:
            Blob data as bytes if found, None if not found

        Raises:
            RuntimeError: If blob service client is not initialized
            Exception: If blob download fails for reasons other than not found
        """
        with self.logger.create_span(
            "AzureStorage.download_blob",
            attributes={
                "service.name": self.service_name,
                "operation.type": "blob_download",
                "storage.container_name": container_name,
                "storage.blob_name": blob_name,
                "storage.account_url": self.account_url
            }
        ):
            if self.blob_service_client is None:
                error_msg = "Blob service client not initialized. Enable blob storage during initialization."
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

            try:
                self.logger.debug(
                    "Downloading blob from Azure Storage",
                    extra={
                        "container_name": container_name,
                        "blob_name": blob_name
                    }
                )

                blob_client = self.blob_service_client.get_blob_client(
                    container=container_name,
                    blob=blob_name
                )

                blob_data = blob_client.download_blob(**kwargs)
                content = blob_data.readall()
                
                self.logger.info(
                    "Blob downloaded successfully",
                    extra={
                        "container_name": container_name,
                        "blob_name": blob_name,
                        "content_length": len(content) if content else 0
                    }
                )
                
                return content

            except ResourceNotFoundError:
                self.logger.warning(
                    f"Blob '{blob_name}' not found in container '{container_name}'",
                    extra={"container_name": container_name, "blob_name": blob_name}
                )
                return None
            except Exception as e:
                self.logger.error(
                    f"Failed to download blob '{blob_name}': {e}",
                    extra={
                        "container_name": container_name,
                        "blob_name": blob_name
                    },
                    exc_info=True
                )
                raise

    def delete_blob(
        self,
        container_name: str,
        blob_name: str,
        **kwargs
    ) -> bool:
        """Delete a blob from Azure Blob Storage.

        Args:
            container_name: Name of the container
            blob_name: Name of the blob to delete
            **kwargs: Additional parameters for blob deletion

        Returns:
            True if blob was deleted successfully

        Raises:
            RuntimeError: If blob service client is not initialized
            Exception: If blob deletion fails
        """
        with self.logger.create_span(
            "AzureStorage.delete_blob",
            attributes={
                "service.name": self.service_name,
                "operation.type": "blob_deletion",
                "storage.container_name": container_name,
                "storage.blob_name": blob_name,
                "storage.account_url": self.account_url
            }
        ):
            if self.blob_service_client is None:
                error_msg = "Blob service client not initialized. Enable blob storage during initialization."
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

            try:
                self.logger.debug(
                    "Deleting blob from Azure Storage",
                    extra={
                        "container_name": container_name,
                        "blob_name": blob_name
                    }
                )

                blob_client = self.blob_service_client.get_blob_client(
                    container=container_name,
                    blob=blob_name
                )

                blob_client.delete_blob(**kwargs)
                
                self.logger.info(
                    "Blob deleted successfully",
                    extra={
                        "container_name": container_name,
                        "blob_name": blob_name
                    }
                )
                
                return True

            except ResourceNotFoundError:
                self.logger.warning(
                    f"Blob '{blob_name}' not found in container '{container_name}' for deletion",
                    extra={"container_name": container_name, "blob_name": blob_name}
                )
                return False
            except Exception as e:
                self.logger.error(
                    f"Failed to delete blob '{blob_name}': {e}",
                    extra={
                        "container_name": container_name,
                        "blob_name": blob_name
                    },
                    exc_info=True
                )
                raise

    def list_blobs(
        self,
        container_name: str,
        name_starts_with: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """List blobs in a container.

        Args:
            container_name: Name of the container
            name_starts_with: Optional prefix to filter blob names
            **kwargs: Additional parameters for listing blobs

        Returns:
            List of blob names

        Raises:
            RuntimeError: If blob service client is not initialized
            Exception: If listing blobs fails
        """
        with self.logger.create_span(
            "AzureStorage.list_blobs",
            attributes={
                "service.name": self.service_name,
                "operation.type": "blob_listing",
                "storage.container_name": container_name,
                "storage.account_url": self.account_url
            }
        ):
            if self.blob_service_client is None:
                error_msg = "Blob service client not initialized. Enable blob storage during initialization."
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

            try:
                self.logger.debug(
                    "Listing blobs from Azure Storage",
                    extra={
                        "container_name": container_name,
                        "name_starts_with": name_starts_with
                    }
                )

                container_client = self.blob_service_client.get_container_client(container_name)
                
                blob_names = []
                for blob in container_client.list_blobs(
                    name_starts_with=name_starts_with,
                    **kwargs
                ):
                    blob_names.append(blob.name)
                
                self.logger.info(
                    "Blobs listed successfully",
                    extra={
                        "container_name": container_name,
                        "blob_count": len(blob_names)
                    }
                )
                
                return blob_names

            except Exception as e:
                self.logger.error(
                    f"Failed to list blobs in container '{container_name}': {e}",
                    extra={"container_name": container_name},
                    exc_info=True
                )
                raise



    # Queue Operations
    def send_message(
        self,
        queue_name: str,
        content: str,
        visibility_timeout: Optional[int] = None,
        time_to_live: Optional[int] = None,
        **kwargs
    ) -> bool:
        """Send a message to an Azure Storage Queue.

        Args:
            queue_name: Name of the queue
            content: Message content
            visibility_timeout: Optional visibility timeout in seconds
            time_to_live: Optional time to live in seconds
            **kwargs: Additional parameters for message sending

        Returns:
            True if message was sent successfully

        Raises:
            RuntimeError: If queue service client is not initialized
            Exception: If message sending fails
        """
        with self.logger.create_span(
            "AzureStorage.send_message",
            attributes={
                "service.name": self.service_name,
                "operation.type": "queue_send_message",
                "storage.queue_name": queue_name,
                "storage.account_url": self.account_url
            }
        ):
            if self.queue_service_client is None:
                error_msg = "Queue service client not initialized. Enable queue storage during initialization."
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

            try:
                self.logger.debug(
                    "Sending message to Azure Storage Queue",
                    extra={
                        "queue_name": queue_name,
                        "message_length": len(content),
                        "visibility_timeout": visibility_timeout,
                        "time_to_live": time_to_live
                    }
                )

                queue_client = self.queue_service_client.get_queue_client(queue_name)
                
                queue_client.send_message(
                    content=content,
                    visibility_timeout=visibility_timeout,
                    time_to_live=time_to_live,
                    **kwargs
                )
                
                self.logger.info(
                    "Message sent successfully",
                    extra={"queue_name": queue_name}
                )
                
                return True

            except Exception as e:
                self.logger.error(
                    f"Failed to send message to queue '{queue_name}': {e}",
                    extra={"queue_name": queue_name},
                    exc_info=True
                )
                raise

    def receive_messages(
        self,
        queue_name: str,
        messages_per_page: int = 1,
        visibility_timeout: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Receive messages from an Azure Storage Queue.

        Args:
            queue_name: Name of the queue
            messages_per_page: Number of messages to receive per page
            visibility_timeout: Optional visibility timeout in seconds
            **kwargs: Additional parameters for message receiving

        Returns:
            List of message dictionaries containing message data

        Raises:
            RuntimeError: If queue service client is not initialized
            Exception: If message receiving fails
        """
        with self.logger.create_span(
            "AzureStorage.receive_messages",
            attributes={
                "service.name": self.service_name,
                "operation.type": "queue_receive_messages",
                "storage.queue_name": queue_name,
                "storage.account_url": self.account_url
            }
        ):
            if self.queue_service_client is None:
                error_msg = "Queue service client not initialized. Enable queue storage during initialization."
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

            try:
                self.logger.debug(
                    "Receiving messages from Azure Storage Queue",
                    extra={
                        "queue_name": queue_name,
                        "messages_per_page": messages_per_page,
                        "visibility_timeout": visibility_timeout
                    }
                )

                queue_client = self.queue_service_client.get_queue_client(queue_name)
                
                messages = []
                for message_page in queue_client.receive_messages(
                    messages_per_page=messages_per_page,
                    visibility_timeout=visibility_timeout,
                    **kwargs
                ):
                    for message in message_page:
                        messages.append({
                            "id": message.id,
                            "content": message.content,
                            "dequeue_count": message.dequeue_count,
                            "insertion_time": message.insertion_time,
                            "expiration_time": message.expiration_time,
                            "pop_receipt": message.pop_receipt
                        })
                
                self.logger.info(
                    "Messages received successfully",
                    extra={
                        "queue_name": queue_name,
                        "message_count": len(messages)
                    }
                )
                
                return messages

            except Exception as e:
                self.logger.error(
                    f"Failed to receive messages from queue '{queue_name}': {e}",
                    extra={"queue_name": queue_name},
                    exc_info=True
                )
                raise

    def delete_message(
        self,
        queue_name: str,
        message_id: str,
        pop_receipt: str,
        **kwargs
    ) -> bool:
        """Delete a message from an Azure Storage Queue.

        Args:
            queue_name: Name of the queue
            message_id: ID of the message to delete
            pop_receipt: Pop receipt of the message
            **kwargs: Additional parameters for message deletion

        Returns:
            True if message was deleted successfully

        Raises:
            RuntimeError: If queue service client is not initialized
            Exception: If message deletion fails
        """
        with self.logger.create_span(
            "AzureStorage.delete_message",
            attributes={
                "service.name": self.service_name,
                "operation.type": "queue_delete_message",
                "storage.queue_name": queue_name,
                "storage.message_id": message_id,
                "storage.account_url": self.account_url
            }
        ):
            if self.queue_service_client is None:
                error_msg = "Queue service client not initialized. Enable queue storage during initialization."
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

            try:
                self.logger.debug(
                    "Deleting message from Azure Storage Queue",
                    extra={
                        "queue_name": queue_name,
                        "message_id": message_id
                    }
                )

                queue_client = self.queue_service_client.get_queue_client(queue_name)
                
                queue_client.delete_message(
                    message=message_id,
                    pop_receipt=pop_receipt,
                    **kwargs
                )
                
                self.logger.info(
                    "Message deleted successfully",
                    extra={
                        "queue_name": queue_name,
                        "message_id": message_id
                    }
                )
                
                return True

            except Exception as e:
                self.logger.error(
                    f"Failed to delete message '{message_id}' from queue '{queue_name}': {e}",
                    extra={
                        "queue_name": queue_name,
                        "message_id": message_id
                    },
                    exc_info=True
                )
                raise



    def test_connection(self) -> bool:
        """Test connection to Azure Storage by attempting to list containers.

        Returns:
            True if connection is successful, False otherwise
        """
        with self.logger.create_span(
            "AzureStorage.test_connection",
            attributes={
                "service.name": self.service_name,
                "operation.type": "connection_test",
                "storage.account_url": self.account_url
            }
        ):
            try:
                self.logger.debug(
                    "Testing Azure Storage connection",
                    extra={"account_url": self.account_url}
                )

                if self.blob_service_client is not None:
                    # Try to list containers (limited to 1) to test connection
                    list(self.blob_service_client.list_containers(results_per_page=1))
                elif self.queue_service_client is not None:
                    # Try to list queues if blob storage is disabled
                    list(self.queue_service_client.list_queues(results_per_page=1))
                elif self.file_service_client is not None:
                    # Try to list shares if queues are disabled
                    list(self.file_service_client.list_shares(results_per_page=1))
                else:
                    self.logger.error("No clients available for connection testing")
                    return False

                self.logger.info("Azure Storage connection test successful")
                return True

            except Exception as e:
                self.logger.warning(
                    f"Azure Storage connection test failed: {e}",
                    extra={"account_url": self.account_url}
                )
                return False

    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for request/transaction tracking.

        Args:
            correlation_id: Unique identifier for transaction correlation
        """
        self.logger.set_correlation_id(correlation_id)

    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID.

        Returns:
            Current correlation ID if set, otherwise None
        """
        return self.logger.get_correlation_id()


def create_azure_storage(
    account_url: str,
    credential: Optional[TokenCredential] = None,
    azure_identity: Optional[AzureIdentity] = None,
    service_name: str = "azure_storage",
    service_version: str = "1.0.0",
    logger: Optional[AzureLogger] = None,
    connection_string: Optional[str] = None,
    enable_blob_storage: bool = True,
    enable_file_storage: bool = True,
    enable_queue_storage: bool = True,
) -> AzureStorage:
    """Factory function to create cached AzureStorage instance.

    Returns existing storage instance if one with same configuration exists.
    Provides a convenient way to create an AzureStorage instance with
    common configuration patterns. If no credential or azure_identity
    is provided, creates a default AzureIdentity instance.

    Args:
        account_url: Azure Storage Account URL
        credential: Azure credential for authentication
        azure_identity: AzureIdentity instance for credential management
        service_name: Service name for tracing context
        service_version: Service version for metadata
        logger: Optional AzureLogger instance
        connection_string: Application Insights connection string
        enable_blob_storage: Enable blob storage operations client
        enable_file_storage: Enable file storage operations client
        enable_queue_storage: Enable queue storage operations client

    Returns:
        Configured AzureStorage instance (cached if available)

    Example:
        # Basic usage with default credential
        storage = create_azure_storage("https://account.blob.core.windows.net/")
        
        # With custom service name and specific features
        storage = create_azure_storage(
            "https://account.blob.core.windows.net/",
            service_name="my_app",
            enable_file_storage=False,
            enable_queue_storage=False
        )
        
        # Note: Containers and queues should be created via infrastructure as code
    """
    # Handle default credential creation before caching
    if credential is None and azure_identity is None:
        # Create default AzureIdentity instance
        from ..mgmt.identity import create_azure_identity
        azure_identity = create_azure_identity(
            service_name=f"{service_name}_identity",
            service_version=service_version,
            connection_string=connection_string,
        )

    # Create cache key from configuration parameters
    # Use object identity for credential objects since they may not be hashable
    cache_key = (
        account_url,
        id(credential) if credential else None,
        id(azure_identity) if azure_identity else None,
        service_name,
        service_version,
        id(logger) if logger else None,
        connection_string,
        enable_blob_storage,
        enable_file_storage,
        enable_queue_storage,
    )

    # Return cached instance if available
    if cache_key in _storage_instances:
        return _storage_instances[cache_key]

    # Create new instance and cache it
    storage_instance = AzureStorage(
        account_url=account_url,
        credential=credential,
        azure_identity=azure_identity,
        service_name=service_name,
        service_version=service_version,
        logger=logger,
        connection_string=connection_string,
        enable_blob_storage=enable_blob_storage,
        enable_file_storage=enable_file_storage,
        enable_queue_storage=enable_queue_storage,
    )
    
    _storage_instances[cache_key] = storage_instance
    return storage_instance 