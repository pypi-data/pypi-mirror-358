import logging

import numpy as np

# Configure logging
logger = logging.getLogger(__name__)


def is_binary_mask(predicted_mask: np.ndarray) -> bool:
    """
    Check if a given mask is binary (contains only 0 and 255 values).

    REQUIREMENT: Ensure the mask is binary.

    Parameters
    ----------
    mask : np.ndarray
        A NumPy array representing the mask to be validated.

    Returns
    -------
    bool
        True if the mask contains only binary values (0 and 255), False otherwise.
    """
    is_binary = np.all(np.isin(predicted_mask, (0, 255)))
    if is_binary:
        logger.info("Requirement met: The mask is binary (only 0s and 255s).")
    else:
        logger.warning("Requirement NOT met: The mask is not binary!")

    return is_binary


def check_size_match(input_image: np.ndarray, predicted_mask: np.ndarray) -> bool:
    """
    Check if the input image and output mask have the same shape.

    REQUIREMENT: Check if the size of the predicted mask matches the input image.

    Parameters
    ----------
    input_image : np.ndarray
        The input image array.
    predicted_mask : np.ndarray
        The predicted_mask array.

    Returns
    -------
    bool
        True if both input and output arrays have the same shape, False otherwise.
    """
    match = input_image.shape == predicted_mask.shape
    if match:
        logger.info("Requirement met: Input and output sizes match.")
    else:
        logger.warning("Requirement NOT met: Input and output sizes do not match!")
        logger.debug(f"Input image shape: {input_image.shape}")
        logger.debug(f"Predicted mask shape: {predicted_mask.shape}")
    return match
