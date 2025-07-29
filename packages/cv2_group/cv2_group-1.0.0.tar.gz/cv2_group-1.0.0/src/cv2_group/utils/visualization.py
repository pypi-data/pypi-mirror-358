import base64
import logging
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
from fastapi import HTTPException
from skimage.morphology import skeletonize

logger = logging.getLogger(__name__)


def _draw_rois_on_image(
    image: np.ndarray,
    rois: List[Tuple[int, int, int, int]],
    color: Tuple[int, int, int] = (0, 255, 0),
) -> np.ndarray:
    """
    Draws rectangular ROIs on a given image.

    Parameters
    ----------
    image : np.ndarray
        The input image (BGR format).
    rois : List[Tuple[int, int, int, int]]
        List of ROIs, each as (x, y, width, height).
    color : Tuple[int, int, int], optional
        Color of the ROI rectangles in BGR format (default is green).

    Returns
    -------
    np.ndarray
        Image with ROIs drawn.
    """
    if image.ndim == 2:  # If grayscale, convert to BGR for color drawing
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    output_image = image.copy()
    for x, y, w, h in rois:
        cv2.rectangle(output_image, (x, y), (x + w, y + h), color, 3)
    return output_image


def _overlay_mask_on_image(
    original_image: np.ndarray, mask: np.ndarray, alpha: float = 0.5
) -> np.ndarray:
    """
    Overlays a binary mask onto the original image with transparency.

    Parameters
    ----------
    original_image : np.ndarray
        The original image (BGR format).
    mask : np.ndarray
        The binary mask (single channel, 0 or 255).
    alpha : float, optional
        Transparency level for the mask overlay, by default 0.5.

    Returns
    -------
    np.ndarray
        The image with the mask overlaid.
    """
    if original_image.ndim == 2:
        original_image = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)

    mask_color = np.zeros_like(original_image)
    # Set mask color to green (0, 255, 0) for the segmented regions
    mask_color[mask == 255] = [0, 255, 0]

    # Blend the mask color with the original image
    overlaid_image = cv2.addWeighted(original_image, 1 - alpha, mask_color, alpha, 0)
    return overlaid_image


def _draw_tip_base_and_path(
    image: np.ndarray,
    analysis_results: List[Dict[str, Any]],
    tip_color: Tuple[int, int, int] = (0, 0, 255),  # Red for Tip
    base_color: Tuple[int, int, int] = (255, 0, 0),  # Blue for Base
    path_color: Tuple[int, int, int] = (0, 255, 255),  # Yellow for Path
) -> np.ndarray:
    """
    Draws tip and base points, and the primary root path on the image.

    Parameters
    ----------
    image : np.ndarray
        The input image (BGR format).
    analysis_results : List[Dict[str, Any]]
        List of raw analysis result dictionaries, each containing 'tip_coords',
        'base_coords', and 'primary_path'.
    tip_color : Tuple[int, int, int], optional
        Color for the tip point, by default Red (BGR).
    base_color : Tuple[int, int, int], optional
        Color for the base point, by default Blue (BGR).
    path_color : Tuple[int, int, int], optional
        Color for the primary path, by default Yellow (BGR).

    Returns
    -------
    np.ndarray
        Image with tip, base, and path drawn.
    """
    if image.ndim == 2:  # If grayscale, convert to BGR for color drawing
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    output_image = image.copy()
    for result in analysis_results:
        # Draw primary path
        if result.get("primary_path"):
            # The path_coords from skimage are (row, col)
            # - need to swap to (col, row) for OpenCV
            path_coords_rc = np.array(result["primary_path"])
            path_coords_xy = path_coords_rc[:, [1, 0]]  # Swap columns (col, row)

            path_coords_xy = path_coords_xy.reshape((-1, 1, 2))
            # Ensure path coordinates are integers before drawing polylines
            path_coords_xy = path_coords_xy.astype(np.int32)
            cv2.polylines(output_image, [path_coords_xy], False, path_color, 2)

        # Draw base
        if result.get("base_coords"):
            base_y, base_x = result["base_coords"]
            # Ensure coordinates are integers
            cv2.circle(output_image, (int(base_x), int(base_y)), 10, base_color, -1)
            cv2.putText(
                output_image,
                "B",
                (int(base_x) + 12, int(base_y) + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                base_color,
                2,
            )

        # Draw tip
        if result.get("tip_coords"):
            tip_y, tip_x = result["tip_coords"]
            # Ensure coordinates are integers
            cv2.circle(output_image, (int(tip_x), int(tip_y)), 10, tip_color, -1)
            cv2.putText(
                output_image,
                "T",
                (int(tip_x) + 12, int(tip_y) + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                tip_color,
                2,
            )
    return output_image


def _image_to_base64(image: np.ndarray) -> str:
    """
    Convert a NumPy array image in BGR format to a base64 encoded PNG string.

    Args:
        image (np.ndarray): Input image in BGR color space.

    Returns:
        str: Base64 encoded PNG image string. Returns empty string if
             the input image is None, empty, or encoding fails.
    """
    if image is None or image.size == 0:
        logger.warning("Attempted to convert empty or None image to base64.")
        return ""
    try:
        _, buffer = cv2.imencode(".png", image)
        return base64.b64encode(buffer).decode("utf-8")
    except Exception as e:
        logger.error(f"Error encoding image to base64: {e}")
        return ""


def _generate_full_size_visualizations(
    original_image_bgr: np.ndarray,
    uncropped_binary_mask: np.ndarray,
    rois_for_analysis: List[Tuple[int, int, int, int]],
    analysis_results_for_display_full_size: List[Dict[str, Any]],
) -> Tuple[str, str, str, str]:
    """
    Generate full-size visualization images as base64-encoded PNG strings.

    This function creates four types of visualizations:
    1. Overlay of the binary mask on the original image with ROI and skeleton
       annotations.
    2. The binary mask image itself (in grayscale).
    3. The original image annotated with regions of interest (ROIs).
    4. The original image annotated with tips, bases, and primary paths.

    Args:
        original_image_bgr (np.ndarray): The original input image in BGR format.
        uncropped_binary_mask (np.ndarray): Binary mask image with pixel values 0 or
            1 (or 0-255).
        rois_for_analysis (List[Tuple[int, int, int, int]]): List of bounding boxes
            for regions of interest.
        analysis_results_for_display_full_size (List[Dict[str, Any]]): Analysis data
            for drawing tips, bases, and paths.
    """
    logger.info("Generating full-size visualizations...")

    # Ensure the mask is 3-channel for overlay if original image is BGR
    # and the mask is 2-channel. If original is grayscale, it's converted
    # to BGR for drawing in _draw_rois_on_image and _draw_tip_base_and_path.

    # Full size mask image (binary, but sent as PNG so it can appear grayscale or B/W)
    # Ensure mask is 0 or 255 for proper display.
    if uncropped_binary_mask.max() == 1:
        display_mask = (uncropped_binary_mask * 255).astype(np.uint8)
    else:
        display_mask = uncropped_binary_mask.astype(np.uint8)
    full_size_mask_image_base64 = _image_to_base64(display_mask)

    # Full size overlay image (mask + original)
    full_size_overlay_image = _overlay_mask_on_image(
        original_image_bgr, uncropped_binary_mask
    )
    # Draw ROIs on overlay (yellow)
    full_size_overlay_image = _draw_rois_on_image(
        full_size_overlay_image,
        rois_for_analysis,
        color=(0, 255, 255),  # Yellow ROIs on overlay
    )
    # Draw all root skeletons (green)
    full_size_overlay_image = draw_all_root_skeletons_on_image(
        full_size_overlay_image, uncropped_binary_mask, color=(0, 255, 0), thickness=2
    )
    # Draw tips/bases/primary paths (yellow for path)
    full_size_overlay_image = _draw_tip_base_and_path(
        full_size_overlay_image,
        analysis_results_for_display_full_size,
        path_color=(0, 255, 255),
    )
    full_size_overlay_image_base64 = _image_to_base64(full_size_overlay_image)

    # Full size ROIs image (only ROIs on original)
    full_size_rois_image = _draw_rois_on_image(original_image_bgr, rois_for_analysis)
    full_size_rois_image_base64 = _image_to_base64(full_size_rois_image)

    # Full size tip/base image (only tip/base/path on original)
    full_size_tip_base_image = _draw_tip_base_and_path(
        original_image_bgr, analysis_results_for_display_full_size
    )
    full_size_tip_base_image_base64 = _image_to_base64(full_size_tip_base_image)

    logger.info("Finished generating full-size visualizations.")
    return (
        full_size_overlay_image_base64,
        full_size_mask_image_base64,
        full_size_rois_image_base64,
        full_size_tip_base_image_base64,
    )


def create_side_by_side_visualization(
    original_image: np.ndarray, blue_mask: np.ndarray, green_mask: np.ndarray
) -> bytes:
    """
    Creates a single image showing two versions of the original image side-by-side,
    one with the blue mask overlay and one with the green mask overlay.

    Args:
        original_image (np.ndarray): The original BGR image.
        blue_mask (np.ndarray): The binary mask from the 'blue' model.
        green_mask (np.ndarray): The binary mask from the 'green' model.

    Returns:
        bytes: The resulting image encoded as PNG bytes.
    """
    # Define colors for the overlays (in BGR format)
    BLUE_COLOR = [255, 0, 0]
    GREEN_COLOR = [0, 255, 0]
    transparency = 0.4

    # Create blue overlay
    img_blue_overlay = original_image.copy()
    blue_color_layer = np.zeros_like(img_blue_overlay, np.uint8)
    blue_color_layer[blue_mask == 1] = BLUE_COLOR
    cv2.addWeighted(
        blue_color_layer,
        transparency,
        img_blue_overlay,
        1 - transparency,
        0,
        img_blue_overlay,
    )
    cv2.putText(
        img_blue_overlay,
        "Blue Model",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    # Create green overlay
    img_green_overlay = original_image.copy()
    green_color_layer = np.zeros_like(img_green_overlay, np.uint8)
    green_color_layer[green_mask == 1] = GREEN_COLOR
    cv2.addWeighted(
        green_color_layer,
        transparency,
        img_green_overlay,
        1 - transparency,
        0,
        img_green_overlay,
    )
    cv2.putText(
        img_green_overlay,
        "Green Model",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    # Combine images
    combined_image = np.hstack((img_blue_overlay, img_green_overlay))

    # Encode to png
    is_success, buffer = cv2.imencode(".png", combined_image)
    if not is_success:
        raise HTTPException(
            status_code=500, detail="Failed to encode comparison image."
        )

    return buffer.tobytes()


def draw_all_root_skeletons_on_image(
    image: np.ndarray,
    binary_mask: np.ndarray,
    color: Tuple[int, int, int] = (255, 0, 255),
    thickness: int = 1,
) -> np.ndarray:
    """
    Overlays all root skeletons (from connected components) on the image.
    Args:
        image: The original image (BGR).
        binary_mask: The binary mask (0/255 or 0/1).
        color: BGR color for skeletons (default magenta).
        thickness: Line thickness.
    Returns:
        Image with all root skeletons overlayed.
    """
    if binary_mask.max() == 1:
        mask = (binary_mask * 255).astype(np.uint8)
    else:
        mask = binary_mask.astype(np.uint8)

    # Connected components
    num_labels, labels = cv2.connectedComponents(mask)
    output = image.copy()
    for label in range(1, num_labels):
        component = (labels == label).astype(np.uint8)
        skeleton = skeletonize(component > 0)
        coords = np.column_stack(np.where(skeleton))
        for y, x in coords:
            cv2.circle(output, (int(x), int(y)), thickness, color, -1)
    return output
