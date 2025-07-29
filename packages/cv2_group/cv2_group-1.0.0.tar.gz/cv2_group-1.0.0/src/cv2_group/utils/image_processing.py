import json
import logging
from typing import List, Optional, Tuple

import cv2
import numpy as np
from fastapi import HTTPException, UploadFile, status

from cv2_group.models.pydantic_models import RoiInput

logger = logging.getLogger(__name__)


async def _process_input_image(file: UploadFile) -> np.ndarray:
    """
    Decodes the uploaded image file and ensures it's in BGR format.
    Raises HTTPException if the image cannot be decoded.

    Parameters
    ----------
    file : UploadFile
        The uploaded image file.

    Returns
    -------
    np.ndarray
        The decoded image as a NumPy array in BGR format.
    """
    contents = await file.read()
    file_bytes = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not decode image. Invalid image file.",
        )

    # Ensure image is 3-channel (BGR) for consistent processing and
    # visualization
    if len(image.shape) == 2:  # Grayscale
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.shape[2] == 4:  # RGBA
        return cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    else:  # Already BGR or another 3-channel format
        return image.copy()


def _process_rois_json(
    rois_json: Optional[str],
) -> Tuple[List[Tuple[int, int, int, int]], List[RoiInput], List[int]]:
    """
    Parses the ROIs JSON string, validates each ROI, and returns lists
    suitable for analysis and response.
    Raises HTTPException for invalid JSON or ROI structure.

    Parameters
    ----------
    rois_json : Optional[str]
        Optional JSON string of ROIs. Each ROI is expected to be
        {'x': int, 'y': int, 'width': int, 'height': int}.

    Returns
    -------
    Tuple[List[Tuple[int, int, int, int]], List[RoiInput], List[int]]
        - rois_for_analysis: List of ROIs as (x, y, width, height) tuples.
        - rois_input_for_response: List of RoiInput Pydantic models.
        - original_roi_indices: List of original indices for each ROI.
    """
    rois_for_analysis: List[Tuple[int, int, int, int]] = []
    rois_input_for_response: List[RoiInput] = []
    original_roi_indices: List[int] = []

    if rois_json:
        try:
            rois_data = json.loads(rois_json)
            for idx, r_dict in enumerate(rois_data):
                # Validate ROI structure using Pydantic
                roi_model = RoiInput(**r_dict)
                rois_for_analysis.append(
                    (roi_model.x, roi_model.y, roi_model.width, roi_model.height)
                )
                rois_input_for_response.append(roi_model)
                original_roi_indices.append(idx)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode ROIs JSON: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ROIs JSON format: {e}",
            )
        except Exception as e:  # Catch Pydantic validation errors or other issues
            logger.error(f"Error parsing ROI data: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ROI structure or data: {e}. "
                "Expected objects with 'x', 'y', 'width', 'height'.",
            )
    else:
        logger.info("No ROIs provided. Analysis results will reflect this.")

    return rois_for_analysis, rois_input_for_response, original_roi_indices
