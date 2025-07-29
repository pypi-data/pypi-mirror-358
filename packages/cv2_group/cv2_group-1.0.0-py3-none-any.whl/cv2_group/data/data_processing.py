import logging
from typing import Tuple

import cv2
import numpy as np
from patchify import patchify, unpatchify

logger = logging.getLogger(__name__)


def crop_image(
    image: np.ndarray,
) -> Tuple[np.ndarray, Tuple[int, int, int, int], Tuple[int, int]]:
    """
    Crops the largest connected component from the image and centers it
    in a white square of size equal to the largest dimension.
    Returns the original bounding box and the offsets used for centering.

    Parameters
    ----------
    image : np.ndarray
        Grayscale image as a 2D NumPy array.

    Returns
    -------
    Tuple[np.ndarray, Tuple[int, int, int, int], Tuple[int, int]]
        - Cropped and centered square image containing the largest component.
        - A tuple (x, y, width, height) representing the bounding box of the
          largest component in the *original* input image.
        - A tuple (x_offset, y_offset) representing the top-left corner
          where the cropped component was placed within the square_image.
    """
    logger.info("Starting image cropping process.")

    # Apply median blur to reduce noise
    blurred_image = cv2.medianBlur(image, 5)

    # Apply thresholding to obtain binary image
    _, binary_image = cv2.threshold(blurred_image, 70, 200, cv2.THRESH_BINARY)

    # Identify connected components and their stats
    _, labels, stats, _ = cv2.connectedComponentsWithStats(binary_image)

    # Find the largest non-background component
    max_area = 0
    max_index = -1
    for i in range(1, stats.shape[0]):
        area = stats[i, 4]
        if area > max_area:
            max_area = area
            max_index = i

    if max_index == -1:
        logger.error("No valid components found in the image.")
        raise ValueError("Could not find any non-background components.")

    # Bounding box of the largest component in the original image
    (
        original_bbox_x,
        original_bbox_y,
        original_bbox_width,
        original_bbox_height,
        _,
    ) = stats[max_index]

    # Determine the size of the square canvas
    size = max(original_bbox_width, original_bbox_height)

    # Create a square canvas and place the component in the center
    # Use 255 (white) for background
    square_image = np.ones((size, size), dtype=np.uint8) * 255
    x_offset = (size - original_bbox_width) // 2
    y_offset = (size - original_bbox_height) // 2

    # Extract the region of interest from the blurred_image
    roi_from_blurred = blurred_image[
        original_bbox_y : original_bbox_y + original_bbox_height,
        original_bbox_x : original_bbox_x + original_bbox_width,
    ]

    # Place the ROI into the center of the square_image
    square_image[
        y_offset : y_offset + original_bbox_height,
        x_offset : x_offset + original_bbox_width,
    ] = roi_from_blurred

    logger.info(
        f"Cropped and centered image to {size}x{size} square. "
        f"Original ROI: ({original_bbox_x}, {original_bbox_y}, "
        f"{original_bbox_width}, {original_bbox_height})."
        f"Offsets in square: ({x_offset}, {y_offset})."
    )

    return (
        square_image,
        (original_bbox_x, original_bbox_y, original_bbox_width, original_bbox_height),
        (x_offset, y_offset),
    )


def crop_image_with_bbox(
    image: np.ndarray,
) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
    """
    Crop the input image to its largest connected component and make it square.

    This function performs the following steps:
    1. Applies a median blur to reduce noise.
    2. Thresholds the image to create a binary mask.
    3. Identifies connected components and selects the largest one.
    4. Crops the image to the bounding box of the largest component.
    5. Pads the crop to make it a square image centered around the object.

    Parameters
    ----------
    image : np.ndarray
        Grayscale input image as a 2D NumPy array.

    Returns
    -------
    square : np.ndarray
        Cropped and square-padded image as a 2D NumPy array.
    bbox : Tuple[int, int, int, int]
        Bounding box (x, y, width, height) of the largest connected component.
    """
    blurred = cv2.medianBlur(image, 5)
    _, binary = cv2.threshold(blurred, 70, 200, cv2.THRESH_BINARY)
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(binary)

    max_index = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
    x, y, w, h = stats[max_index, cv2.CC_STAT_LEFT : cv2.CC_STAT_HEIGHT + 1]
    size = max(w, h)

    square = np.ones((size, size), dtype=np.uint8) * 255
    x_offset = (size - w) // 2
    y_offset = (size - h) // 2
    square[y_offset : y_offset + h, x_offset : x_offset + w] = blurred[
        y : y + h, x : x + w
    ]

    return square, (x, y, w, h)


def pad_image(
    image: np.ndarray, patch_size: int
) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
    """
    Pads the image so its dimensions are divisible by patch_size by adding
    borders symmetrically.

    Parameters
    ----------
    image : np.ndarray
        Grayscale image as a 2D NumPy array.
    patch_size : int
        Size of the patches the image will be divided into.

    Returns
    -------
    Tuple[np.ndarray, Tuple[int, int, int, int]]
        Zero-padded image with height and width divisible by patch_size.
        A tuple containing padding sizes (top, bottom, left, right).
    """
    logger.info("Padding image to make its dimensions divisible by patch size.")

    # Get original image dimensions
    h, w = image.shape

    # Calculate the padding needed for each dimension
    height_padding = ((h // patch_size) + 1) * patch_size - h
    width_padding = ((w // patch_size) + 1) * patch_size - w

    # Split padding evenly between top/bottom and left/right
    top_padding = height_padding // 2
    bottom_padding = height_padding - top_padding
    left_padding = width_padding // 2
    right_padding = width_padding - left_padding

    # Apply zero padding to the image using OpenCV
    padded_image = cv2.copyMakeBorder(
        image,
        top_padding,
        bottom_padding,
        left_padding,
        right_padding,
        cv2.BORDER_CONSTANT,
        value=0,
    )

    logger.info(
        f"Padded image from ({h}, {w}) to {padded_image.shape} with "
        f"top={top_padding}, bottom={bottom_padding}, "
        f"left={left_padding}, right={right_padding}."
    )

    return padded_image, (top_padding, bottom_padding, left_padding, right_padding)


def pad_image_alternative(
    image: np.ndarray, patch_size: int
) -> Tuple[np.ndarray, Tuple[int, int]]:
    """
    Pad the image so its dimensions are divisible by `patch_size`.

    This function pads the bottom and right sides of a grayscale image
    using a constant value (255) so that its height and width are
    evenly divisible by the specified patch size.

    Parameters
    ----------
    image : np.ndarray
        Grayscale input image as a 2D NumPy array.
    patch_size : int
        Desired size of patches to divide the image into.

    Returns
    -------
    padded : np.ndarray
        Padded image with dimensions divisible by `patch_size`.
    padding : Tuple[int, int]
        Tuple of padding applied to height and width respectively: (pad_h, pad_w).
    """
    h, w = image.shape
    pad_h = (patch_size - h % patch_size) % patch_size
    pad_w = (patch_size - w % patch_size) % patch_size

    padded = cv2.copyMakeBorder(
        image, 0, pad_h, 0, pad_w, cv2.BORDER_CONSTANT, value=255
    )

    return padded, (pad_h, pad_w)


def create_patches(
    image: np.ndarray, patch_size: int
) -> Tuple[np.ndarray, int, int, np.ndarray]:
    """
    Splits a grayscale image into non-overlapping square RGB patches of the
    given size. The grayscale image is converted to 3-channel RGB before
    patching, as expected by the model input.

    Parameters
    ----------
    image : np.ndarray
        Grayscale image as a 2D NumPy array.
    patch_size : int
        The height and width of each square patch.

    Returns
    -------
    np.ndarray
        4D array of shape (num_patches, patch_size, patch_size, 3), containing
        RGB patches.
    int
        Number of patch rows (i).
    int
        Number of patch columns (j).
    np.ndarray
        RGB version of the padded input image.
    """
    logger.info("Starting patch creation from grayscale image.")

    # Convert the grayscale image to a 3-channel RGB image by stacking.
    # This is done because the model is trained with 3-channel input.
    padded_image_rgb = np.stack((image.squeeze(),) * 3, axis=-1)

    # Create non-overlapping patches using patchify
    patches = patchify(padded_image_rgb, (patch_size, patch_size, 3), step=patch_size)

    # Extract the number of patches in vertical (i) and horizontal (j) direction
    i = patches.shape[0]
    j = patches.shape[1]

    # Reshape the patches to a 4D array (num_patches, patch_size, patch_size, 3)
    patches = patches.reshape(-1, patch_size, patch_size, 3)

    logger.info(
        f"Created {len(patches)} patches of size {patch_size}x{patch_size}. "
        f"Grid: {i} rows x {j} cols."
    )

    return patches, i, j, padded_image_rgb


def create_patches_alternative(
    image: np.ndarray, patch_size: int
) -> Tuple[np.ndarray, int, int]:
    """
    Split the image into non-overlapping patches of a given size.

    This function divides a 2D image into square patches of size
    `patch_size` x `patch_size`, ignoring any remainder areas that
    do not form a complete patch.

    Parameters
    ----------
    image : np.ndarray
        Grayscale input image as a 2D NumPy array.
    patch_size : int
        Size of each square patch.

    Returns
    -------
    patches : np.ndarray
        Array of image patches with shape (num_patches, patch_size, patch_size).
    num_rows : int
        Number of patches along the image height.
    num_cols : int
        Number of patches along the image width.
    """
    h, w = image.shape
    patches = [
        image[y : y + patch_size, x : x + patch_size]
        for y in range(0, h, patch_size)
        for x in range(0, w, patch_size)
        if image[y : y + patch_size, x : x + patch_size].shape
        == (patch_size, patch_size)
    ]

    return np.array(patches), h // patch_size, w // patch_size


def unpatch_image(
    preds: np.ndarray, i: int, j: int, padded_image_shape: Tuple[int, int]
) -> np.ndarray:
    """
    Reconstructs the original grayscale prediction image from patches.

    Parameters
    ----------
    preds : np.ndarray
        Raw prediction output from the model. Expected shape can be
        (num_patches, patch_height, patch_width, num_channels) or
        (num_patches, patch_height, patch_width).
    i, j : int
        Patch grid dimensions, representing the number of patches along the
        height and width.
    padded_image_shape : Tuple[int, int]
        The (height, width) of the padded image from which patches were created.
        Used to determine the full output shape for unpatchify.

    Returns
    -------
    np.ndarray
        The reconstructed 2D grayscale prediction image.
    """
    logger.info("Reconstructing image from patches.")

    if preds.ndim == 4:
        # If output includes a channel dimension (e.g., (N, 128, 128, 1))
        # Remove the channel dimension for unpatchify
        patch_h = preds.shape[1]
        patch_w = preds.shape[2]
        # Squeeze the channel dimension if it's 1
        preds_for_unpatch = preds.squeeze(axis=-1)
        # Reshape to (i, j, patch_h, patch_w)
        preds_reshaped = preds_for_unpatch.reshape(i, j, patch_h, patch_w)
    elif preds.ndim == 3:
        # If output is already (N, 128, 128)
        patch_h = preds.shape[1]
        patch_w = preds.shape[2]
        preds_reshaped = preds.reshape(i, j, patch_h, patch_w)
    else:
        raise ValueError(
            f"Unexpected preds dimension: {preds.ndim}. " "Expected 3 or 4 dimensions."
        )

    # Reconstruct the image using the unpatchify function
    predicted_mask = unpatchify(preds_reshaped, padded_image_shape)

    logger.info(f"Predicted mask shape: {predicted_mask.shape}")

    return predicted_mask


def remove_padding(
    image: np.ndarray, top: int, bottom: int, left: int, right: int
) -> np.ndarray:
    """
    Removes padding from an image based on the given top, bottom, left, and
    right values.

    Parameters
    ----------
    image : np.ndarray
        The padded image.
    top : int
        Number of pixels to remove from the top.
    bottom : int
        Number of pixels to remove from the bottom.
    left : int
        Number of pixels to remove from the left.
    right : int
        Number of pixels to remove from the right.

    Returns
    -------
    np.ndarray
        The cropped image without padding.
    """
    return image[top : image.shape[0] - bottom, left : image.shape[1] - right]


def uncrop_mask(
    cropped_mask: np.ndarray,
    original_image_shape: Tuple[int, int],
    original_bbox: Tuple[int, int, int, int],
    square_offsets: Tuple[int, int],
) -> np.ndarray:
    """
    Reconstructs a mask from its cropped and centered version back to the
    original image's dimensions.

    Parameters
    ----------
    cropped_mask : np.ndarray
        The mask that corresponds to the square_image produced by crop_image
        (after remove_padding). Its shape should be (size, size) where size
        is max(original_bbox_width, original_bbox_height).
    original_image_shape : Tuple[int, int]
        A tuple (height, width) representing the dimensions of the image
        *before* any cropping by crop_image.
    original_bbox : Tuple[int, int, int, int]
        A tuple (x, y, width, height) representing the bounding box of the
        largest component in the *original* input image, as returned by
        crop_image.
    square_offsets : Tuple[int, int]
        A tuple (x_offset, y_offset) representing the top-left corner
        where the cropped component was placed within the square_image,
        as returned by crop_image.

    Returns
    -------
    np.ndarray
        The mask resized and placed back onto a canvas of the original
        image's dimensions.
    """
    logger.info("Starting uncropping of the mask to original image dimensions.")

    original_height, original_width = original_image_shape
    (
        original_bbox_x,
        original_bbox_y,
        original_bbox_width,
        original_bbox_height,
    ) = original_bbox
    x_offset, y_offset = square_offsets

    # Create an empty canvas of the original image's size
    # Assuming mask values are 0 or 255. Use 0 for background.
    full_size_mask = np.zeros(original_image_shape, dtype=np.uint8)

    # Extract the relevant portion of the cropped_mask that corresponds
    # to the actual root component (removing the centering padding from
    # crop_image)
    roi_mask = cropped_mask[
        y_offset : y_offset + original_bbox_height,
        x_offset : x_offset + original_bbox_width,
    ]

    # Place this roi_mask onto the full_size_mask at the original
    # bounding box coordinates
    full_size_mask[
        original_bbox_y : original_bbox_y + original_bbox_height,
        original_bbox_x : original_bbox_x + original_bbox_width,
    ] = roi_mask

    logger.info(f"Uncropped mask shape: {full_size_mask.shape}")
    return full_size_mask
