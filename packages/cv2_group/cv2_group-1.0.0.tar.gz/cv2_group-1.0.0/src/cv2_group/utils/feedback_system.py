import base64
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from azure.ai.ml import MLClient
from azure.storage.blob import BlobClient
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

# Feedback System Constants
MAX_FEEDBACK_PER_IMAGE = 10

FEEDBACK_JSON_BLOB = "feedback/feedback_data.json"
FEEDBACK_IMAGES_PREFIX = "feedback/images"


class FeedbackImageData(BaseModel):
    """Model for storing image data in feedback (now stores blob paths or URLs)"""

    original_image: str = Field(..., description="Blob path or URL to original image")
    overlay_image: str = Field(..., description="Blob path or URL to overlay image")
    mask_image: str = Field(..., description="Blob path or URL to mask image")
    drawing_image: str = Field(
        ..., description="Blob path or URL to drawing area image"
    )


class FeedbackAnalysisData(BaseModel):
    """Model for storing analysis table data in feedback"""

    roi_data: List[Dict[str, Any]] = Field(..., description="ROI analysis results")
    image_filename: str = Field(..., description="Original image filename")


class FeedbackSubmission(BaseModel):
    """Model for feedback submission"""

    image_data: FeedbackImageData = Field(
        ..., description="All 4 images from analysis (base64 strings)"
    )
    analysis_data: FeedbackAnalysisData = Field(..., description="Analysis table data")
    message: str = Field(
        ..., max_length=500, description="User feedback message (max 500 chars)"
    )
    user_identifier: Optional[str] = Field(None, description="Optional user identifier")
    model_source: str = Field(
        ..., description="Which model the feedback is for: 'local' or 'azure'"
    )


class FeedbackEntry(BaseModel):
    """Complete feedback entry with metadata"""

    id: str = Field(..., description="Unique feedback entry ID")
    image_data: FeedbackImageData = Field(
        ..., description="All 4 images from analysis (blob paths/URLs)"
    )
    analysis_data: FeedbackAnalysisData = Field(..., description="Analysis table data")
    message: str = Field(..., description="User feedback message")
    user_identifier: Optional[str] = Field(None, description="Optional user identifier")
    timestamp: datetime = Field(..., description="Submission timestamp")
    image_filename: str = Field(..., description="Original image filename for grouping")
    model_source: str = Field(
        ..., description="Which model the feedback is for: 'local' or 'azure'"
    )


def get_blob_client(ml_client: MLClient, blob_name: str) -> BlobClient:
    """
    Create and return a BlobClient for a specific blob in the default datastore.

    Args:
        ml_client (MLClient): Azure ML client instance.
        blob_name (str): Name of the blob to access.

    Returns:
        BlobClient: Client to interact with the specified blob.
    """
    datastore = ml_client.datastores.get_default()
    storage_account_url = f"https://{datastore.account_name}.blob.core.windows.net"
    return BlobClient(
        account_url=storage_account_url,
        container_name=datastore.container_name,
        blob_name=blob_name,
        credential=ml_client._credential,
    )


def get_blob_url(ml_client: MLClient, blob_name: str) -> str:
    """
    Construct and return the URL for a blob in the default datastore.

    Args:
        ml_client (MLClient): Azure ML client instance.
        blob_name (str): Name of the blob.

    Returns:
        str: URL to access the specified blob.
    """
    datastore = ml_client.datastores.get_default()
    storage_account_url = f"https://{datastore.account_name}.blob.core.windows.net"
    return f"{storage_account_url}/{datastore.container_name}/{blob_name}"


def load_feedback_data(ml_client: MLClient) -> List[Dict[str, Any]]:
    """
    Load feedback data from a JSON file stored in Azure blob storage.

    Args:
        ml_client (MLClient): Azure ML client instance.

    Returns:
        List[Dict[str, Any]]: List of feedback entries, with timestamps parsed
        as datetime objects.
        Returns an empty list if loading fails.
    """
    blob_client = get_blob_client(ml_client, FEEDBACK_JSON_BLOB)
    try:
        data = blob_client.download_blob().readall()
        feedback_list = json.loads(data.decode("utf-8"))
        for entry in feedback_list:
            if "timestamp" in entry:
                entry["timestamp"] = datetime.fromisoformat(entry["timestamp"])
        return feedback_list
    except Exception as e:
        logger.error(f"Error loading feedback data from Azure: {e}")
        return []


def save_feedback_data(ml_client: MLClient, data: List[Dict[str, Any]]) -> None:
    """
    Save feedback data to a JSON file in Azure blob storage.

    Args:
        ml_client (MLClient): Azure ML client instance.
        data (List[Dict[str, Any]]): Feedback data to save. Timestamps will be converted
        to ISO strings.
    """
    blob_client = get_blob_client(ml_client, FEEDBACK_JSON_BLOB)
    serializable_data = []
    for entry in data:
        entry_copy = entry.copy()
        if "timestamp" in entry_copy and isinstance(entry_copy["timestamp"], datetime):
            entry_copy["timestamp"] = entry_copy["timestamp"].isoformat()
        serializable_data.append(entry_copy)
    blob_client.upload_blob(
        json.dumps(serializable_data, ensure_ascii=False).encode("utf-8"),
        overwrite=True,
    )


def save_base64_image_to_blob(
    ml_client: MLClient, base64_str: str, feedback_id: str, image_type: str
) -> str:
    """
    Save a base64-encoded image to Azure blob storage and return its URL.

    Args:
        ml_client (MLClient): Azure ML client instance.
        base64_str (str): Base64-encoded PNG image string.
        feedback_id (str): Unique identifier for the feedback entry.
        image_type (str): Type/category of the image (e.g., original_image).

    Returns:
        str: URL of the saved image blob.
    """
    img_data = base64.b64decode(base64_str)
    blob_name = f"{FEEDBACK_IMAGES_PREFIX}/{feedback_id}_{image_type}.png"
    blob_client = get_blob_client(ml_client, blob_name)
    blob_client.upload_blob(img_data, overwrite=True)
    return get_blob_url(ml_client, blob_name)


def add_feedback_entry(
    ml_client: MLClient, feedback: FeedbackSubmission, image_filename: str
) -> str:
    """
    Add a new feedback entry, saving associated images and managing storage limits.

    Args:
        ml_client (MLClient): Azure ML client instance.
        feedback (FeedbackSubmission): Feedback data including images and analysis.
        image_filename (str): Name of the image file related to this feedback.

    Returns:
        str: Unique identifier of the new feedback entry.
    """
    feedback_data = load_feedback_data(ml_client)
    feedback_id = str(uuid.uuid4())
    image_paths = {}
    for key in ["original_image", "overlay_image", "mask_image", "drawing_image"]:
        base64_str = getattr(feedback.image_data, key)
        image_paths[key] = save_base64_image_to_blob(
            ml_client, base64_str, feedback_id, key
        )

    new_entry = FeedbackEntry(
        id=feedback_id,
        image_data=FeedbackImageData(**image_paths),
        analysis_data=feedback.analysis_data,
        message=feedback.message,
        user_identifier=feedback.user_identifier,
        timestamp=datetime.now(),
        image_filename=image_filename,
        model_source=feedback.model_source,
    )

    feedback_data.insert(0, new_entry.dict())

    # Clean up old feedback entries if we exceed the limit per image/model
    image_model_entries = [
        entry
        for entry in feedback_data
        if entry["image_filename"] == image_filename
        and entry["model_source"] == feedback.model_source
    ]
    if len(image_model_entries) > MAX_FEEDBACK_PER_IMAGE:
        entries_to_remove = len(image_model_entries) - MAX_FEEDBACK_PER_IMAGE
        removed_count = 0
        for i in range(len(feedback_data) - 1, -1, -1):
            if (
                feedback_data[i]["image_filename"] == image_filename
                and feedback_data[i]["model_source"] == feedback.model_source
            ):
                # Delete images from Azure blob
                for key in [
                    "original_image",
                    "overlay_image",
                    "mask_image",
                    "drawing_image",
                ]:
                    try:
                        blob_name = (
                            feedback_data[i]["image_data"][key]
                            .split(f".blob.core.windows.net/")[-1]
                            .split("/", 1)[-1]
                        )
                        blob_client = get_blob_client(ml_client, blob_name)
                        blob_client.delete_blob()
                    except Exception as e:
                        logger.warning(f"Failed to remove image blob: {e}")
                feedback_data.pop(i)
                removed_count += 1
                if removed_count >= entries_to_remove:
                    break

    save_feedback_data(ml_client, feedback_data)
    return feedback_id


def get_feedback_entries(ml_client: MLClient) -> List[Dict[str, Any]]:
    """
    Retrieve all feedback entries (newest first) from Azure blob storage.

    Args:
        ml_client (MLClient): Azure ML client instance.

    Returns:
        List[Dict[str, Any]]: List of all feedback entries.
    """
    return load_feedback_data(ml_client)


def get_feedback_entries_for_image(
    ml_client: MLClient, image_filename: str
) -> List[Dict[str, Any]]:
    """
    Retrieve feedback entries for a specific image (newest first).

    Args:
        ml_client (MLClient): Azure ML client instance.
        image_filename (str): Filename of the image to filter feedback entries.

    Returns:
        List[Dict[str, Any]]: List of feedback entries related to the specified image.
    """
    all_entries = load_feedback_data(ml_client)
    return [entry for entry in all_entries if entry["image_filename"] == image_filename]


def delete_feedback_entry(ml_client: MLClient, feedback_id: str) -> bool:
    """
    Delete a specific feedback entry and its associated images from Azure blob storage.

    Args:
        ml_client (MLClient): Azure ML client instance.
        feedback_id (str): Unique identifier of the feedback entry to delete.

    Returns:
        bool: True if deletion was successful, False if entry was not found.
    """
    feedback_data = load_feedback_data(ml_client)

    # Find and remove the entry
    entry_to_delete = None
    for entry in feedback_data:
        if entry["id"] == feedback_id:
            entry_to_delete = entry
            break
    if not entry_to_delete:
        return False  # Entry not found

    # Delete images from Azure blob
    for key in ["original_image", "overlay_image", "mask_image", "drawing_image"]:
        try:
            blob_name = (
                entry_to_delete["image_data"][key]
                .split(f".blob.core.windows.net/")[-1]
                .split("/", 1)[-1]
            )
            blob_client = get_blob_client(ml_client, blob_name)
            blob_client.delete_blob()
        except Exception as e:
            logger.warning(f"Failed to remove image blob: {e}")

    # Remove entry from list
    feedback_data = [entry for entry in feedback_data if entry["id"] != feedback_id]

    # Save updated data
    save_feedback_data(ml_client, feedback_data)
    return True


def initialize_feedback_storage(ml_client: MLClient):
    """
    Initialize feedback storage by creating an empty JSON file in Azure blob storage.

    Args:
        ml_client (MLClient): Azure ML client instance.
    """
    blob_client = get_blob_client(ml_client, FEEDBACK_JSON_BLOB)
    blob_client.upload_blob(
        json.dumps([], ensure_ascii=False).encode("utf-8"), overwrite=True
    )
