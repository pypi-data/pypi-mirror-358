import base64
import io
import json
import logging
import zlib
from typing import List, Optional, Tuple

import cv2
import numpy as np
import tensorflow as tf
from azure.ai.ml import MLClient
from azure.ai.ml.entities import ManagedOnlineEndpoint
from fastapi import HTTPException, status
from keras import backend as K
from PIL import Image

from cv2_group.utils.image_helpers import decode_b64_png_to_ndarray

logger = logging.getLogger(__name__)


def recall(y_true, y_pred):
    """
    Compute the recall score for binary classification.

    Recall is the ratio of true positives to the total number of actual
    positives: Recall = TP / (TP + FN)

    Parameters
    ----------
    y_true : tensor
        Ground truth binary labels (0 or 1).
    y_pred : tensor
        Predicted binary labels (0 or 1).

    Returns
    -------
    tensor
        Recall score as a scalar tensor.
    """
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    return true_positives / (possible_positives + K.epsilon())


def precision(y_true, y_pred):
    """
    Compute the precision score for binary classification.

    Precision is the ratio of true positives to the total number of predicted
    positives: Precision = TP / (TP + FP)

    Parameters
    ----------
    y_true : tensor
        Ground truth binary labels (0 or 1).
    y_pred : tensor
        Predicted binary labels (0 or 1).

    Returns
    -------
    tensor
        Precision score as a scalar tensor.
    """
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    return true_positives / (predicted_positives + K.epsilon())


def f1(y_true, y_pred):
    """
    Compute the F1 score for binary classification.

    The F1 score is the harmonic mean of precision and recall:
    F1 = 2 * (precision * recall) / (precision + recall)

    This version includes a safeguard against division by zero to avoid
    returning NaN.

    Parameters
    ----------
    y_true : tensor
        Ground truth binary labels (0 or 1).
    y_pred : tensor
        Predicted binary labels (0 or 1).

    Returns
    -------
    tensor
        F1 score (scalar tensor).
    """
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    prec = precision(y_true, y_pred)
    rec = recall(y_true, y_pred)
    return 2 * ((prec * rec) / (prec + rec + K.epsilon()))


def numpy_to_base64_png(image_array: np.ndarray) -> str:
    """Encodes a NumPy array (image) into a base64 string as PNG."""
    is_success, buffer = cv2.imencode(".png", image_array)
    if not is_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not encode image to PNG.",
        )
    return base64.b64encode(buffer).decode("utf-8")


def _transform_rois_to_cropped_coords(
    rois_original: List[Tuple[int, int, int, int]],
    original_bbox: Tuple[int, int, int, int],
    square_offsets: Tuple[int, int],
) -> List[Tuple[int, int, int, int]]:
    """
    Transforms ROI coordinates from the original image's coordinate system
    to the coordinate system of the cropped and centered square image.

    Parameters
    ----------
    rois_original : List[Tuple[int, int, int, int]]
        A list of ROIs, where each ROI is (x, y, width, height) relative to
        the *original* input image.
    original_bbox : Tuple[int, int, int, int]
        The bounding box (x, y, width, height) of the largest component in the
        *original* input image, as returned by crop_image.
    square_offsets : Tuple[int, int]
        The offsets (x_offset, y_offset) used to place the original_bbox's
        content within the square_image, as returned by crop_image.

    Returns
    -------
    List[Tuple[int, int, int, int]]
        A list of transformed ROIs, where each ROI is (x, y, width, height)
        relative to the *cropped and centered square image*.
    """
    logger.info("Transforming ROIs to cropped image coordinates.")

    transformed_rois = []
    original_bbox_x, original_bbox_y, _, _ = original_bbox
    square_offset_x, square_offset_y = square_offsets

    for roi_x, roi_y, roi_width, roi_height in rois_original:
        # Calculate ROI's position relative to the original bounding box's
        # top-left. This is the coordinate within the "content" that was
        # moved to the square_image.
        relative_x = roi_x - original_bbox_x
        relative_y = roi_y - original_bbox_y

        # Add the square_offsets to get the position in the square_image.
        transformed_x = relative_x + square_offset_x
        transformed_y = relative_y + square_offset_y

        # The width and height of the ROI remain the same.
        transformed_width = roi_width
        transformed_height = roi_height

        transformed_rois.append(
            (transformed_x, transformed_y, transformed_width, transformed_height)
        )

    logger.info(f"Transformed {len(rois_original)} ROIs.")
    return transformed_rois


def shift_traffic(
    ml_client: MLClient,
    online_endpoint_name: str,
    blue_percent: int,
    green_percent: int,
) -> None:
    """
    Shifts traffic between blue and green deployments for an Azure ML online endpoint.

    Ensures the traffic distribution between 'blue' and 'green'
    deployments sums to 100%

    Args:
        ml_client (MLClient): Authenticated Azure ML client instance.
        online_endpoint_name (str): Name of the online endpoint to modify.
        blue_percent (int): Traffic percentage to route to the 'blue' deployment.
        green_percent (int): Traffic percentage to route to the 'green' deployment.

    Raises:
        ValueError: If blue_percent + green_percent != 100.

    Example:
        >>> shift_traffic(client, "my-endpoint", blue_percent=80, green_percent=20)
    """
    if blue_percent + green_percent != 100:
        raise ValueError("Traffic percentages must add up to 100.")

    logger.info(
        "Shifting traffic: %d%% to 'blue', %d%% to 'green' for endpoint '%s'",
        blue_percent,
        green_percent,
        online_endpoint_name,
    )

    try:
        endpoint: ManagedOnlineEndpoint = ml_client.online_endpoints.get(
            name=online_endpoint_name
        )
        endpoint.traffic = {"blue": blue_percent, "green": green_percent}
        ml_client.begin_create_or_update(endpoint).result()

        logger.info(
            "Traffic successfully shifted. New distribution: %s", endpoint.traffic
        )
    except Exception as e:
        logger.exception(
            "Failed to shift traffic for endpoint '%s': %s",
            online_endpoint_name,
            str(e),
        )


# I've removed the unpack_model_response function
# because it is already in image_processing


def encode_mask_for_json(mask: Optional[np.ndarray]) -> Optional[str]:
    """
    Encode a numpy array mask into a base64-encoded PNG string suitable for JSON
    serialization.

    Args:
        mask (Optional[np.ndarray]): Binary or grayscale mask array. Can have values
            0-1 or 0-255.

    Returns:
        Optional[str]: Base64-encoded PNG string representation of the mask, or None
            if mask is None.
    """
    if mask is None:
        return None
    # Ensure mask is in a displayable format (e.g., 0-255 uint8)
    display_mask = (
        (mask * 255).astype(np.uint8) if mask.max() <= 1.0 else mask.astype(np.uint8)
    )
    img = Image.fromarray(display_mask)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def unpack_model_response(base64_encoded_compressed_response_string: str) -> Tuple:
    """
    Unpack and decode a model response from a base64-encoded, compressed JSON string.

    Args:
        base64_encoded_compressed_response_string (str):
            Base64 encoded, zlib-compressed JSON string containing the model's response.

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
