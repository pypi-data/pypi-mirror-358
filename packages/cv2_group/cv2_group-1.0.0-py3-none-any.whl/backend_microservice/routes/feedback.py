import logging
import os
from datetime import datetime

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
from fastapi import APIRouter, HTTPException, Response

from cv2_group.utils.feedback_system import (
    FeedbackSubmission,
    add_feedback_entry,
    delete_feedback_entry,
    get_feedback_entries,
    get_feedback_entries_for_image,
)

logger = logging.getLogger(__name__)
router = APIRouter()

FEEDBACK_IMAGES_FOLDER = "feedback/images"


def get_ml_client():
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    workspace_name = os.getenv("AZURE_WORKSPACE_NAME")
    credential = DefaultAzureCredential()
    return MLClient(credential, subscription_id, resource_group, workspace_name)


@router.post("/feedback/submit")
async def submit_feedback(feedback: FeedbackSubmission, image_filename: str):
    """Submit feedback for an analyzed image"""
    try:
        logger.info(f"Feedback submission received for image: {image_filename}")
        if len(feedback.message.strip()) == 0:
            raise HTTPException(
                status_code=400, detail="Feedback message cannot be empty"
            )
        if len(feedback.message) > 500:
            raise HTTPException(
                status_code=400, detail="Feedback message exceeds 500 character limit"
            )
        ml_client = get_ml_client()
        feedback_id = add_feedback_entry(ml_client, feedback, image_filename)
        logger.info(f"Feedback submitted successfully with ID: {feedback_id}")
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id,
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to submit feedback: {str(e)}"
        )


def feedback_entry_with_urls(entry):
    return entry  # URLs are already direct blob URLs in new system


@router.get("/feedback/list")
async def get_feedback_list():
    """Get all feedback entries (newest first)"""
    try:
        ml_client = get_ml_client()
        feedback_entries = get_feedback_entries(ml_client)
        logger.info(f"Retrieved {len(feedback_entries)} feedback entries")
        return {
            "feedback_entries": feedback_entries,
            "total_count": len(feedback_entries),
        }
    except Exception as e:
        logger.error(f"Error retrieving feedback list: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve feedback: {str(e)}"
        )


@router.get("/feedback/image/{image_filename}")
async def get_feedback_for_image(image_filename: str):
    """Get feedback entries for a specific image (newest first)"""
    try:
        ml_client = get_ml_client()
        feedback_entries = get_feedback_entries_for_image(ml_client, image_filename)
        logger.info(
            f"Retrieved {len(feedback_entries)} feedback entries for "
            f"image: {image_filename}"
        )
        return {
            "feedback_entries": feedback_entries,
            "image_filename": image_filename,
            "total_count": len(feedback_entries),
        }
    except Exception as e:
        logger.error(
            f"Error retrieving feedback for image {image_filename}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve feedback: {str(e)}"
        )


@router.delete("/feedback/{feedback_id}")
async def delete_feedback(feedback_id: str):
    """Delete a specific feedback entry (admin function)"""
    try:
        ml_client = get_ml_client()
        success = delete_feedback_entry(ml_client, feedback_id)
        if not success:
            raise HTTPException(status_code=404, detail="Feedback entry not found")
        logger.info(f"Feedback entry {feedback_id} deleted successfully")
        return {"message": "Feedback entry deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting feedback {feedback_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to delete feedback: {str(e)}"
        )


@router.get("/proxy-blob-image/{image_name}")
async def proxy_blob_image(image_name: str):
    """Proxy an image from Azure Blob Storage to the browser (no CORS needed)."""
    try:
        ml_client = get_ml_client()
        datastore = ml_client.datastores.get_default()
        container_name = datastore.container_name
        account_url = f"https://{datastore.account_name}.blob.core.windows.net"
        from azure.storage.blob import BlobServiceClient

        blob_service_client = BlobServiceClient(
            account_url, credential=DefaultAzureCredential()
        )
        container_client = blob_service_client.get_container_client(container_name)
        blob_path = f"{FEEDBACK_IMAGES_FOLDER}/{image_name}"
        print(f"[proxy-blob-image] Blob path: {blob_path}")

        blob_service_client = BlobServiceClient(
            account_url, credential=DefaultAzureCredential()
        )
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_path)
        if not blob_client.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        image_bytes = blob_client.download_blob().readall()
        return Response(content=image_bytes, media_type="image/png")
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback

        print("[proxy-blob-image] General Exception occurred")
        traceback.print_exc()
        logger.error(f"Error proxying blob image {image_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")
