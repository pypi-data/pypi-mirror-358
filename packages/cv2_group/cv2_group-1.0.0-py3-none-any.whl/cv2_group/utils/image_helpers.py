import base64
import json
import logging
import zlib
from typing import Any, Dict, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def _transform_analysis_results_for_cropped_view(
    raw_result: Dict[str, Any],
    original_bbox: Tuple[int, int, int, int],
    square_offsets: Tuple[int, int],
) -> Dict[str, Any]:
    """
    Transforms tip, base, and primary path coordinates within a raw analysis
    result dictionary from original image coordinates to cropped image
    coordinates.
    NOTE: This function is still present but its output is no longer used
    for visualization in the frontend or API response. It remains if there's
    a future need for cropped-space analysis data.
    """
    transformed_result = raw_result.copy()

    # OpenCV uses (x, y) which corresponds to (col, row).
    # Our coordinates are (row, col) which corresponds to (y, x).
    # original_bbox is (x, y, width, height) = (col, row, width, height)
    # square_offsets is (x_offset, y_offset) = (col_offset, row_offset)

    if transformed_result.get("tip_coords"):
        original_tip_y, original_tip_x = transformed_result["tip_coords"]
        transformed_tip_x = (original_tip_x - original_bbox[0]) + square_offsets[0]
        transformed_tip_y = (original_tip_y - original_bbox[1]) + square_offsets[1]
        transformed_result["tip_coords"] = [transformed_tip_y, transformed_tip_x]

    if transformed_result.get("base_coords"):
        original_base_y, original_base_x = transformed_result["base_coords"]
        transformed_base_x = (original_base_x - original_bbox[0]) + square_offsets[0]
        transformed_base_y = (original_base_y - original_bbox[1]) + square_offsets[1]
        transformed_result["base_coords"] = [transformed_base_y, transformed_base_x]

    if transformed_result.get("primary_path"):
        transformed_path = []
        for row, col in transformed_result["primary_path"]:
            transformed_col = (col - original_bbox[0]) + square_offsets[0]
            transformed_row = (row - original_bbox[1]) + square_offsets[1]
            transformed_path.append([transformed_row, transformed_col])
        transformed_result["primary_path"] = transformed_path

    return transformed_result


def unpack_model_response(base64_encoded_compressed_response_string: str) -> Tuple:
    """
    Unpack and decode a model response from a base64-encoded, compressed JSON string.

    Args:
        base64_encoded_compressed_response_string (str):
            Base64 encoded, zlib-compressed JSON string containing the model's response data.

    Returns:
        Tuple:
            cropped_image_for_prediction (np.ndarray):
                Cropped image for prediction.
            uncropped_binary_mask (np.ndarray):
                Full-size binary mask (uint8).
            original_bbox (Any):
                Original bounding box coordinates from the response.
            square_offsets (Any):
                Offset values for cropping/square adjustments.
            binary_mask_cropped_square (np.ndarray):
                Binary mask cropped to a square (uint8).

    Raises:
        Exception:
            If decompression, decoding, or parsing fails.
    """
    try:
        compressed_bytes = zlib.decompress(
            base64.b64decode(base64_encoded_compressed_response_string)
        )
        decompressed_json_string = compressed_bytes.decode("utf-8")
        response_payload = json.loads(decompressed_json_string)

        cropped_image_for_prediction = decode_b64_png_to_ndarray(
            response_payload["cropped_image_for_prediction_b64_png"]
        )
        uncropped_binary_mask = decode_b64_png_to_ndarray(
            response_payload["uncropped_binary_mask_b64_png"]
        ).astype(np.uint8)
        binary_mask_cropped_square = decode_b64_png_to_ndarray(
            response_payload["binary_mask_cropped_square_b64_png"]
        ).astype(np.uint8)
        original_bbox = response_payload["original_bbox"]
        square_offsets = response_payload["square_offsets"]

        return (
            cropped_image_for_prediction,
            uncropped_binary_mask,
            original_bbox,
            square_offsets,
            binary_mask_cropped_square,
        )
    except Exception as e:
        logger.error(f"Error unpacking model response: {type(e).__name__}: {e}")
        raise


def decode_b64_png_to_ndarray(b64_string: str) -> np.ndarray:
    """
    Decode a base64-encoded PNG image string into a NumPy ndarray.

    Args:
        b64_string (str): Base64 encoded PNG image string.

    Returns:
        np.ndarray: Decoded image as a NumPy array with original image channels
            and depth preserved.
    """
    img_bytes = base64.b64decode(b64_string)
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    return img
