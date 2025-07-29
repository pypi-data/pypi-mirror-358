import os

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

FEEDBACK_FOLDER = "feedback"
FEEDBACK_IMAGES_FOLDER = f"{FEEDBACK_FOLDER}/images"
FEEDBACK_JSON_BLOB = f"{FEEDBACK_FOLDER}/feedback_data.json"


def get_container_client():
    """
    Create and return an Azure Blob Storage container client along with
    the storage account URL and container name.

    Returns:
        Tuple[ContainerClient, str, str]: The container client, storage account URL,
        and container name.
    """
    _credential = DefaultAzureCredential()
    ml_client = MLClient(
        _credential,
        subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
        resource_group_name=os.getenv("AZURE_RESOURCE_GROUP"),
        workspace_name=os.getenv("AZURE_WORKSPACE_NAME"),
    )
    default_datastore = ml_client.datastores.get_default()
    container_name = default_datastore.container_name
    account_url = f"https://{default_datastore.account_name}.blob.core.windows.net"
    blob_service_client = BlobServiceClient(account_url, credential=_credential)
    return (
        blob_service_client.get_container_client(container_name),
        account_url,
        container_name,
    )


def upload_blob(blob_path: str, data: bytes, overwrite: bool = True):
    """
    Upload data to a blob in the Azure Blob Storage container.

    Args:
        blob_path (str): Path of the blob within the container.
        data (bytes): Data to upload.
        overwrite (bool, optional): Whether to overwrite the blob if it exists.
        Defaults to True.
    """
    container_client, _, _ = get_container_client()
    blob_client = container_client.get_blob_client(blob_path)
    blob_client.upload_blob(data, overwrite=overwrite)


def download_blob(blob_path: str) -> bytes:
    """
    Download and return the contents of a blob from Azure Blob Storage.

    Args:
        blob_path (str): Path of the blob within the container.

    Returns:
        bytes: The downloaded blob data.
    """
    container_client, _, _ = get_container_client()
    blob_client = container_client.get_blob_client(blob_path)
    return blob_client.download_blob().readall()


def blob_exists(blob_path: str) -> bool:
    """
    Check if a blob exists in the Azure Blob Storage container.

    Args:
        blob_path (str): Path of the blob within the container.

    Returns:
        bool: True if the blob exists, False otherwise.
    """
    container_client, _, _ = get_container_client()
    blob_client = container_client.get_blob_client(blob_path)
    return blob_client.exists()


def list_blobs_in_folder(folder: str):
    """
    List all blobs within a specified folder (prefix)
    in the Azure Blob Storage container.

    Args:
        folder (str): The prefix/folder path to list blobs under.

    Returns:
        List[str]: List of blob names under the specified folder.
    """
    container_client, _, _ = get_container_client()
    return [b.name for b in container_client.list_blobs(name_starts_with=folder)]


def delete_blob(blob_path: str):
    """
    Delete a blob from the Azure Blob Storage container.

    Args:
        blob_path (str): Path of the blob within the container.
    """
    container_client, _, _ = get_container_client()
    blob_client = container_client.get_blob_client(blob_path)
    blob_client.delete_blob()


def get_blob_url(blob_path: str) -> str:
    """
    Generate the full URL for a blob in the Azure Blob Storage container.

    Args:
        blob_path (str): Path of the blob within the container.

    Returns:
        str: Full URL to access the blob.
    """
    _, account_url, container_name = get_container_client()
    return f"{account_url}/{container_name}/{blob_path}"
