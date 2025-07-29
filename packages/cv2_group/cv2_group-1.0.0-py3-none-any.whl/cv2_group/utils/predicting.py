import logging
from typing import Any, Tuple

import cv2
import numpy as np

from cv2_group.data.data_processing import (
    create_patches,
    crop_image,
    pad_image,
    remove_padding,
    uncrop_mask,
    unpatch_image,
)
from cv2_group.utils.binary import ensure_binary_mask
from cv2_group.utils.configuration import PATCH_SIZE

logger = logging.getLogger(__name__)


def predict_root(patches: np.ndarray, model: Any) -> np.ndarray:
    """
    Performs root segmentation prediction using the loaded model.

    Parameters
    ----------
    patches : np.ndarray
        Array of image patches (pre-processed for the model).
    model : Any
        The loaded Keras/TensorFlow model.

    Returns
    -------
    np.ndarray
        The prediction output from the model.
    """
    # Assuming model expects input scaled to 0-1
    preds = model.predict(patches / 255)
    return preds


def _prepare_image_for_model(
    image: np.ndarray, patch_size: int
) -> Tuple[
    np.ndarray,
    Tuple[int, int],
    Tuple[int, int, int, int],
    Tuple[int, int, int, int],
    Tuple[int, int],
]:
    """
    Prepares the input image for model prediction by converting to grayscale,
    cropping, padding, and creating patches.

    Parameters
    ----------
    image : np.ndarray
        The input image as a NumPy array (can be grayscale or BGR).
    patch_size : int
        The size of the patches the image will be divided into.

    Returns
    -------
    Tuple[
        np.ndarray,            # Patches ready for prediction
        Tuple[int, int],       # Padded image shape (height, width)
        Tuple[int, int, int, int], # Padding details (top, bottom, left, right)
        Tuple[int, int, int, int], # Original bounding box of largest component
        Tuple[int, int]        # Offsets within the square image
    ]
    """
    if len(image.shape) == 3:
        image_for_cropping = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image_for_cropping = image.copy()

    cropped_img_for_pred, original_bbox, square_offsets = crop_image(image_for_cropping)

    padded_image, padding_details = pad_image(cropped_img_for_pred, patch_size)

    patches, i, j, _ = create_patches(padded_image, patch_size)

    # Return i and j for unpatching, but not the full rgb_image
    # as its shape is sufficient
    return (
        patches,
        padded_image.shape,
        padding_details,
        original_bbox,
        square_offsets,
    )


def _reconstruct_and_uncrop_mask(
    preds: np.ndarray,
    padded_image_shape: Tuple[int, int],
    padding_details: Tuple[int, int, int, int],
    original_bbox: Tuple[int, int, int, int],
    square_offsets: Tuple[int, int],
    original_image_shape: Tuple[int, int],
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Reconstructs the predicted mask from patches, removes padding, binarizes,
    and uncrops it back to the original image dimensions.

    Parameters
    ----------
    preds : np.ndarray
        Raw prediction output from the model.
    padded_image_shape : Tuple[int, int]
        Shape of the image after padding.
    padding_details : Tuple[int, int, int, int]
        Padding applied (top, bottom, left, right).
    original_bbox : Tuple[int, int, int, int]
        Bounding box of the largest component in the original image.
    square_offsets : Tuple[int, int]
        Offsets within the square image.
    original_image_shape : Tuple[int, int]
        Shape of the original input image.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        - uncropped_binary_mask: The mask in the original image dimensions.
        - binary_mask_cropped_square: The mask in the cropped square
                                      (padded) dimensions.
    """
    top, bottom, left, right = padding_details
    i = padded_image_shape[0] // PATCH_SIZE
    j = padded_image_shape[1] // PATCH_SIZE

    predicted_mask_padded = unpatch_image(preds, i, j, padded_image_shape)
    predicted_mask_cropped = remove_padding(
        predicted_mask_padded, top, bottom, left, right
    )

    binary_mask_cropped_square = ensure_binary_mask(predicted_mask_cropped)

    uncropped_binary_mask = uncrop_mask(
        binary_mask_cropped_square,
        original_image_shape,
        original_bbox,
        square_offsets,
    )

    return uncropped_binary_mask, binary_mask_cropped_square


def predict_from_array(
    image: np.ndarray, original_image_shape: Tuple[int, int], model: Any
) -> Tuple[
    np.ndarray, np.ndarray, Tuple[int, int, int, int], Tuple[int, int], np.ndarray
]:
    """
    Encapsulates the prediction logic for a single image, now returning
    the cropped image used for prediction, the binary mask uncropped
    back to the original image's dimensions, the cropping parameters,
    and the binary mask *before* uncropping (for cropped visualizations).

    Parameters
    ----------
    image : np.ndarray
        The input image as a NumPy array (can be grayscale or BGR).
    original_image_shape : Tuple[int, int]
        The (height, width) of the image *before* any cropping by crop_image.
    model : Any
        The globally loaded Keras/TensorFlow model.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, Tuple[int, int, int, int], Tuple[int, int], np.ndarray]

        - cropped_image_for_prediction: The square image actually fed into
          the model (before padding).

        - uncropped_binary_mask: The predicted binary mask, uncropped and
          resized to the original_image_shape.

        - original_bbox: Bounding box (x, y, width, height) of the largest
          component in the *original* input image.

        - square_offsets: Offsets (x_offset, y_offset) used to place
          the component within the square_image.

        - binary_mask_cropped_square: The binary mask *before* uncropping
          (i.e., matching the cropped_image_for_prediction size).
    """
    # Extract cropped_image_for_prediction separately
    # as it's needed for return but not directly in the new
    # _prepare_image_for_model output.
    if len(image.shape) == 3:
        image_for_cropping = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image_for_cropping = image.copy()

    cropped_image_for_prediction, original_bbox, square_offsets = crop_image(
        image_for_cropping
    )

    patches, padded_image_shape, padding_details, _, _ = _prepare_image_for_model(
        image, PATCH_SIZE
    )

    preds = predict_root(patches, model)

    uncropped_binary_mask, binary_mask_cropped_square = _reconstruct_and_uncrop_mask(
        preds,
        padded_image_shape,
        padding_details,
        original_bbox,
        square_offsets,
        original_image_shape,
    )

    return (
        cropped_image_for_prediction,
        uncropped_binary_mask,
        original_bbox,
        square_offsets,
        binary_mask_cropped_square,
    )
