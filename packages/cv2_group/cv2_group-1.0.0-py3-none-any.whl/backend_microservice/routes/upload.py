import base64
import logging
import os
from datetime import datetime
from typing import List

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from cv2_group.data.data_ingestion import (
    rename_pairs,
    upload_data,
    upload_to_azure_datastore,
)
from cv2_group.utils.api_models import SaveImageRequest
from cv2_group.utils.azure_integration import get_azure_datastore, is_azure_available

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/save-image")
async def save_image_endpoint(request: SaveImageRequest):
    """
    Endpoint to save a base64 encoded image to the server.
    """
    try:
        image_bytes = base64.b64decode(request.image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_UNCHANGED)

        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not decode image data.",
            )

        date_str = datetime.today().strftime("%Y-%m-%d")
        safe_username = "".join(
            c for c in request.username if c.isalnum() or c in ("_", "-")
        ).strip()
        if not safe_username:
            safe_username = "unknown_user"

        save_dir = "saved_images"
        os.makedirs(save_dir, exist_ok=True)

        file_name = f"{date_str}_{safe_username}_{request.image_type}.png"
        file_path = os.path.join(save_dir, file_name)

        cv2.imwrite(file_path, image)
        logger.info(f"Saved image to: {file_path}")

        return {
            "message": f"Image '{file_name}' saved successfully.",
            "path": file_path,
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to save image: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save image: {e}",
        )


@router.post("/upload-root-data/")
async def upload_root_data(
    images: List[UploadFile] = File(..., description="List of image files to upload."),
    masks: List[UploadFile] = File(..., description="List of mask files to upload."),
):
    """
    Uploads new image and mask data to Azure ML Datastore for retraining.
    Requires AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET
    environment variables to be set for Service Principal Authentication.
    """
    if not is_azure_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure ML Workspace connection not established. "
            "Check backend logs for authentication errors and ensure "
            "AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET "
            "environment variables are correctly set.",
        )

    try:
        logger.info(f"Received {len(images)} images and {len(masks)} masks for upload.")

        # Use the actual upload_data function
        pairs = upload_data(images, masks)

        if not pairs:  # pairs is now a dict, so check if it's empty
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No matching image-mask pairs found. "
                "Ensure filenames match (e.g., 'image.png' and 'image_root_mask.png').",
            )

        renamed = rename_pairs(pairs)
        datastore = get_azure_datastore()
        # Use the actual upload_to_azure_datastore function
        uploaded_azure_paths = upload_to_azure_datastore(pairs, renamed, datastore)

        return {"status": "Success", "uploaded_files": uploaded_azure_paths}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error during data upload to Azure: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload data to Azure: {e}",
        )
